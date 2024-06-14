# Abstract storage repository classes for user data that is stored on disk: Users, Members, Logs
# Contains a base "Repository" class and the subclasses "FileRepository" and "SQLiteRepository" for storage in a simple file and in an SQLite database respectively

import data.forms
import data.fields
import data.rules
import auth.user
import auth.logging
import storage.encryption
import json

class Repository:
    """Abstract repository class"""

    def __init__(self):
        self.form = data.forms.Form()
        self.name = self.__class__.__name__
        self.idField = None # Can be overwritten by subclass or kept to use Nth item
    

    # Default roles (all "none" unless overwritten by subclasses)
    def canRead(self, id):
        """Role that can read the item with this id, or can list all available items (if id is None)"""
        return "none"
    def canInsert(self):
        """Role that can insert new items"""
        return "none"
    def canUpdate(self, id):
        """Role that can update item with this id"""
        return "none"
    def canDelete(self, id):
        """Role that can delete item with this id"""
        return "none"
    def canChange(self, id, newValues):
        """Role that can make the given changes to the model (newValues contains only the fields that were changed in case of update). This is useful if only some fields are permitted to be changed"""
        return self.canInsert() if id is None else self.canUpdate(id)
    

    # Logic methods to be implemented by subclasses
    def _list(self, offset, limit):
        """Implement to list {limit} items starting from {offset}"""
        pass
    def _one(self, id):
        """Implement to find specified item"""
        pass
    def _add(self, model):
        """Implement to add the (pre-validated) model"""
        pass
    def _replace(self, id, model):
        """Implement to replace the specified item with the (pre-validated) model"""
        pass
    def _remove(self, id):
        """Implement to remove the specified item"""
        pass
    

    def validate(self, action, model):
        """Validate form model and log all validation errors"""

        if self.idField is not None and self.idField not in model:
            auth.logging.log(f"Attempt to {action} invalid data in {self.name} (field: '{self.idField}'): Missing ID-field", True)
        if self.form.validate(model):
            return True
        for field in self.form.errors:
            for error in self.form.errors[field]:
                auth.logging.log(f"Attempt to {action} invalid data in {self.name} (field: '{field}'): {error}", True)
        return False
    

    def readAll(self, offset = 0, limit = 20):
        """Read all items up to {limit} starting from {offset}"""

        if not auth.user.requireAccess(self.canRead(None), f"Unauthorized ReadAll call in {self.name}", True):
            return None # User has no access
        
        items = self._list(offset, limit)

        # Return only validated items (errors will be logged by self.validate)
        return { id: item for id, item in items.items() if self.validate("read invalid data", item) }


    def readOne(self, id):
        """Read one item by ID (what 'ID' means depends on the {idField} property)"""

        if not auth.user.requireAccess(self.canRead(id), f"Unauthorized ReadOne call in {self.name}", True):
            return None # User has no access
        
        item = self._one(id)

        if item is None:
            fieldName = "item number" if self.idField is None else self.idField
            auth.logging.log(f"Error reading in {self.name}: there is no {fieldName} '{id}'")
            return None
        
        if not self.validate("read invalid data", item):
            # This item is invalid (errors have been logged by self.validate)
            return None
        
        return item
    

    def insert(self, model):
        """Insert a data model as a new item"""

        if not auth.user.requireAccess(self.canInsert(), f"Unauthorized Insert call in {self.name}", True):
            return False # User has no access (and that is suspicious)
        
        if not auth.user.requireAccess(self.canChange(None, model), f"Insert call with illegal changes in {self.name}", True):
            return False # User has no access (and that is suspicious)
        
        newRule = None
        if self.idField is not None and self.idField in self.form.fields:
            # If we have an ID field, check for duplicate values
            duplicate = self._one(model[self.idField])
            if duplicate is not None:
                newRule = data.rules.duplicateValue(model[self.idField])(self.form.fields[self.idField].name)
                self.form.fields[self.idField].rules.append(newRule)

        if not self.validate("insert", model):
            # Form model is not valid (errors have been logged during validation)
            if newRule is not None:
                self.form.fields[self.idField].rules.remove(newRule)
            return False
        
        if newRule is not None:
            self.form.fields[self.idField].rules.remove(newRule)

        return self._add(model)
    

    def update(self, id, model):
        """Update the specified id with a new data model (unspecified fields will be unchanged)"""

        if not auth.user.requireAccess(self.canUpdate(id), f"Unauthorized Update call in {self.name} (id: {id})", True):
            return False # User has no access (and that is suspicious)

        item = self._one(id)

        if item is None:
            fieldName = "item number" if self.idField is None else self.idField
            auth.logging.log(f"Error updating in {self.name}: there is no {fieldName} '{id}'")
            return None
        
        changes = {}
        for field in model:
            if self.idField is not None and field == self.idField and model[field] != item[field]:
                auth.logging.log(f"Error updating in {self.name}: {fieldName} cannot be changed (is ID-field)")
                return False

            if model[field] is not None and (field not in item or item[field] != model[field]):
                # Update all item fields from the new model (but do not allow updating the ID field and ignore fields with None value)
                item[field] = model[field]
                changes[field] = model[field]

        if not auth.user.requireAccess(self.canChange(id, changes), f"Update call with illegal changes in {self.name} (id: {id})", True):
            return False # User has no access (and that is suspicious)

        if not self.validate("update", item):
            # Form model is not valid (errors have been logged during validation)
            return False
        
        return self._replace(model)
    
    
    def delete(self, id):
        """Delete the specified id"""

        if not auth.user.requireAccess(self.canDelete(id), f"Unauthorized Delete call in {self.name} (id: {id})", True):
            return False # User has no access (and that is suspicious)

        item = self._one(id)

        if item is None:
            fieldName = "item number" if self.idField is None else self.idField
            auth.logging.log(f"Error deleting in {self.name}: there is no {fieldName} '{id}'")
            return None
        
        return self._remove(id)
    

class FileRepository(Repository):
    """Repository class that represents lines in a file"""

    def __init__(self, path):
        super().__init__()
        self.path = path


    def _add(self, model):
        """Insert a new line into a file"""

        try:
            line = storage.encryption.encrypt(json.dumps(model)) + "\n"
            open(self.path, "a").write(line)
        except Exception as e:
            auth.logging.log(f"Error writing to file {self.path}: " + str(e), True)
            return False
        
        return True


    def _list(self, offset, limit):
        """List all items in the repository (from offset X with a limit of Y)"""
        
        try:
            content = open(self.path, "r").read()
            content = content.strip("\n").split("\n")
            l = 0
            items = {}
            for line in content:
                l += 1 # Line number
                if l <= offset:
                    # Skip "offset" number of lines
                    continue
                if offset + l > limit:
                    # Over the limit
                    break
                model = json.loads(line)
                if self.idField is not None and self.idField in model:
                    items[model[self.idField]] = model
                else:
                    items[l] = model
            return items

        except Exception as e:
            auth.logging.log(f"Error reading from file {self.path}: " + str(e), True)
            return {}
        

    def _one(self, id):
        """Get one item in the repository (by id)"""
    
        try:
            content = open(self.path, "r").read()
            content = content.strip("\n").split("\n")
            l = 0
            for line in content:
                l += 1 # Line number
                if self.idField is None and l != id:
                    # Skip to the correct line number (only possible if there is no ID field)
                    continue
                model = json.loads(line)
                if self.idField is None:
                    # We've found it (by line number)
                    return model
                elif self.idField in model and model[self.idField] == id:
                    # We've found it (by ID field)
                    return model
                elif self.idField is not None:
                    # ID field unexpectedly not included in the validated model (configuration error)
                    auth.logging.log(f"Error reading in {self.name}: validated model does not contain ID field '{self.idField}'")
                    continue
            # If we're still here, the item wasn't found
            return None

        except Exception as e:
            auth.logging.log(f"Error reading from file {self.path}: " + str(e), True)
            return None
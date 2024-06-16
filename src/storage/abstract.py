# Abstract storage repository classes for user data that is stored on disk: Users, Members, Logs
# Contains a base "Repository" class and the subclasses "FileRepository" and "SQLiteRepository" for storage in a simple file and in an SQLite database respectively

import validation.forms
import validation.fields
import validation.rules
import authentication.user
import authentication.logging
import storage.encryption
import json
import os
import re

class Repository:
    """Abstract repository class"""

    def __init__(self):
        self.form = validation.forms.Form()
        self.name = re.sub(r'([a-z])([A-Z])', r"\1 \2", self.__class__.__name__) # ClassName with added spaces ("ClassName" => "Class Name")
        self.idField = None # Can be overwritten by subclass or kept to use Nth item
    

    # Default roles (all "none" unless overwritten by subclasses)
    def readRole(self, id):
        """Role that can read the item with this id, or can list all available items (if id is None)"""
        return "none"
    def insertRole(self):
        """Role that can insert new items"""
        return "none"
    def updateRole(self, id, item):
        """Role that can update item with this id"""
        return "none"
    def deleteRole(self, id, item):
        """Role that can delete item with this id"""
        return "none"
    
    def fieldCheck(self, field, item, value):
        """Check if user is permitted to set field"""
        return value # Should return the value the field should be set to, or None if not permitted to be set/changed. The current values are available in model (which is None on insert)

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
            authentication.logging.log(f"{action} invalid data in {self.name}", f"Field '{self.idField}'): Missing ID-field", True)
            return False
        if self.form.validate(model):
            return True
        for field in self.form.fields:
            if field in self.form.errors:
                for error in self.form.errors[field]:
                    authentication.logging.log(f"{action} invalid data in {self.name}", f"Field '{field}': {error}", True)
            elif self.form.fields[field] is None:
                authentication.logging.log(f"{action} invalid data in {self.name}", f"Field '{field}': value is not set", True)
        return False
    

    def readAll(self, offset = 0, limit = 20):
        """Read all items up to {limit} starting from {offset}"""

        if not authentication.user.requireAccess(self.readRole(None, None), f"Unauthorized read of all {self.name}", f"Offset: {offset}, Limit: {limit}", True):
            return None # User has no access
        
        authentication.logging.log(f"Read all {self.name}", f"Offset: {offset}, Limit: {limit}")
        
        items = self._list(offset, limit)

        # Return only validated items (errors will be logged by self.validate)
        return { id: item for id, item in items.items() if self.validate("Read", item) and self.readRole(id, item) }
    

    def readInternal(self, id):
        """Read one item by ID (what 'ID' means depends on the {idField} property), for internal use without access checking"""

        fieldName = "Line number" if self.idField is None else self.idField

        item = self._one(id)

        if item is None:
            authentication.logging.log(f"Error reading in {self.name}", f"There is no {fieldName}: {id}")
            return None
        
        if not self.validate("Read", item):
            # This item is invalid (errors have been logged by self.validate)
            return None
        
        return item
    

    def exists(self, id):
        """Check if item with ID exists"""
        return self._one(id) is not None


    def readOne(self, id):
        """Read one item by ID (what 'ID' means depends on the {idField} property), with access checking"""

        fieldName = "Line number" if self.idField is None else self.idField

        item = self.readInternal(id)

        if not authentication.user.requireAccess(self.readRole(id, item), f"Unauthorized read from {self.name}", f"{fieldName}: {id}", True):
            return None # User has no access
        
        authentication.logging.log(f"Read from {self.name}", f"{fieldName}: {id}")
        
        return item
    

    def insert(self, model):
        """Insert a data model as a new item"""

        if model is None:
            return False # No model given

        if not authentication.user.requireAccess(self.insertRole(), f"Unauthorized insert in {self.name}", f"Data: {str(model)}", True):
            return False # User has no access
        
        authentication.logging.log(f"Insert into {self.name}", f"Data: {str(model)}")
        
        newRule = None
        if self.idField is not None and self.idField in self.form.fields:
            # If we have an ID field, check for duplicate values
            duplicate = self.exists(model[self.idField])
            if duplicate:
                newRule = validation.rules.duplicateValue(model[self.idField])(self.form.fields[self.idField].name)
                self.form.fields[self.idField].rules.append(newRule)

        if not self.validate("Insert", model):
            # Form model is not valid (errors have been logged during validation)
            if newRule is not None:
                self.form.fields[self.idField].rules.remove(newRule)
            return False
        
        if newRule is not None:
            self.form.fields[self.idField].rules.remove(newRule)

        for field in model:
            # Check if field values are permitted to be set
            newValue = self.fieldCheck(field, None, model[field])
            if newValue is None:
                authentication.logging.log(f"Insert error in {self.name}", f"{field} cannot be set. Data: {str(model)}", True)
                return False
            if newValue != model[field]:
                authentication.logging.log(f"Insert error in {self.name}", f"{field} should be '{newValue}'. Data: {str(model)}", True)
                model[field] = newValue

        return self._add(model)
    

    def update(self, id, model):
        """Update the specified id with a new data model (unspecified fields will be unchanged)"""

        if model is None:
            return False # No model given
        
        fieldName = "Line number" if self.idField is None else self.idField

        item = self.readInternal(id)
        
        if not authentication.user.requireAccess(self.updateRole(id, item), f"Unauthorized update in {self.name}", f"{fieldName}: {id}, Data: {str(model)}", True):
            return False # User has no access
        
        authentication.logging.log(f"Update {self.name}", f"{fieldName}: {id}, Data: {str(model)}")

        if item is None:
            authentication.logging.log(f"Update error in {self.name}", f"{fieldName} '{id}' not found")
            return None
        
        changes = {}
        for field in model:
            if self.idField is not None and field == self.idField and model[field] != item[field]:
                authentication.logging.log(f"Update error in {self.name}", f"{fieldName} cannot be changed because it is the ID field", True)
                return False
            
            if model[field] is not None and (field not in item or item[field] != model[field]):
                # Update all item fields from the new model (but do not allow updating the ID field and ignore fields with None value)
                item[field] = model[field]
                changes[field] = model[field]

        if not self.validate("Update", item):
            # Form model is not valid (errors have been logged during validation)
            return False
        
        for field in changes:
            # Check if field values are permitted to be set
            newValue = self.fieldCheck(field, item, changes[field])
            if newValue is None:
                authentication.logging.log(f"Update error in {self.name}", f"{field} cannot be set. Data: {str(changes)}", True)
                return False
            if newValue != model[field]:
                authentication.logging.log(f"Update error in {self.name}", f"{field} should be '{newValue}'. Data: {str(changes)}", True)
                model[field] = newValue
        
        return self._replace(id, model)
    
    
    def delete(self, id):
        """Delete the specified id"""

        fieldName = "Line number" if self.idField is None else self.idField
        
        exists = self.exists(id)

        if not exists:
            authentication.logging.log(f"Delete error in {self.name}", f"{fieldName} '{id}' not found")
            return None

        if not authentication.user.requireAccess(self.deleteRole(id, self.readInternal(id) if exists else None), f"Unauthorized delete from {self.name}", f"{fieldName}: {id}", True):
            return False # User has no access
        
        authentication.logging.log(f"Delete from {self.name}", f"{fieldName}: {id}")
        
        return self._remove(id)
    

class FileRepository(Repository):
    """Repository class that represents lines in a file"""

    def __init__(self, path):
        super().__init__()
        self.path = path


    def _list(self, offset, limit):
        """List all items in the repository (from offset X with a limit of Y)"""
        
        try:
            if not os.path.exists(self.path):
                # There is nothing to read
                return {}
            with open(self.path, "r") as file:
                file.seek(0)
                content = file.read()
            content = content.strip("\n").split("\n")
            l = 0
            items = {}
            for line in content:
                l += 1 # Line number
                if l <= offset:
                    # Skip "offset" number of lines
                    continue
                if l > offset + limit:
                    # Over the limit
                    break
                try:
                    # Try to decrypt line and parse as JSON
                    model = json.loads(storage.encryption.decrypt(line))
                except:
                    # Invalid JSON or decryption failed
                    authentication.logging.log("Data parsing", "Raw data: " + str(line), True)
                    continue
                if self.idField is not None and self.idField in model:
                    items[model[self.idField]] = model
                else:
                    items[l] = model
            return items

        except Exception as e:
            authentication.logging.log(f"File read error", f"File: {self.path}, Error: {str(e)}", True)
            return {}
        

    def _one(self, id):
        """Get one item in the repository (by id)"""
    
        try:
            if not os.path.exists(self.path):
                # There is nothing to read
                return None
            with open(self.path, "r") as file:
                file.seek(0)
                content = file.read()
            content = content.strip("\n").split("\n")
            l = 0
            for line in content:
                l += 1 # Line number
                if self.idField is None and l != id:
                    # Skip to the correct line number (only possible if there is no ID field)
                    continue
                try:
                    # Try to decrypt line and parse as JSON
                    model = json.loads(storage.encryption.decrypt(line))
                except:
                    # Invalid JSON or decryption failed
                    authentication.logging.log("Data parsing", "Raw data: " + str(line), True)
                    continue
                if self.idField is None:
                    # We've found it (by line number)
                    return model
                elif self.idField in model and str(model[self.idField]).upper() == str(id).upper():
                    # We've found it (by ID field)
                    return model
                elif self.idField is not None and self.idField not in model:
                    # ID field unexpectedly not included in the validated model (configuration error)
                    authentication.logging.log(f"Validation error in {self.name}", f"Validated model does not contain ID field {self.idField}: {str(model)}", True)
                    continue

            # If we're still here, the item wasn't found
            return None

        except Exception as e:
            authentication.logging.log(f"File read error", f"File: {self.path}, Error: {str(e)}", True)
            return None
        

    def _add(self, model):
        """Insert a new line into a file"""

        try:
            line = storage.encryption.encrypt(json.dumps(model)) + "\n"
            with open(self.path, "a") as file:
                file.write(line)
        except Exception as e:
            authentication.logging.log(f"File write error", f"File: {self.path}, Error: {str(e)}", True)
            return False
        
        return True
    

    def _replace(self, id, model):
        """Replace/update a line in the file (by id)"""
    
        try:

            if not os.path.exists(self.path):
                # There is nothing to read
                return False
            with open(self.path, "r") as file:
                file.seek(0)
                content = file.read()
            content = content.strip("\n").split("\n")
            l = 0
            found = False
            newContent = ""

            for line in content:
                l += 1 # Line number 
                if found == True or (self.idField is None and l != id):
                    # Keep the content of this line if we've already found or have yet to reach the correct line number (only possible if there is no ID field)
                    newContent += line + "\n"
                    continue
                try:
                    # Try to decrypt line and parse as JSON
                    lineModel = json.loads(storage.encryption.decrypt(line))
                except:
                    # Invalid JSON or decryption failed
                    authentication.logging.log("Data parsing", "Raw data: " + str(line), True)
                    continue
                if self.idField is None or (self.idField in lineModel and lineModel[self.idField] == id):
                    # We've found it: don't keep this line but save the new content
                    newContent += storage.encryption.encrypt(json.dumps(model)) + "\n"
                    found = True
                    continue
                elif self.idField is not None and self.idField not in model:
                    # ID field unexpectedly not included in the validated model (configuration error)
                    authentication.logging.log(f"Validation error in {self.name}", f"Validated model does not contain ID field {self.idField}: {str(lineModel)}", True)
                # If we get here it's not yet found, keep this line as-is and try the next one
                newContent += line + "\n"
            
            if found == False:
                # The line to update was not found
                return False
            
            with open(self.path, "w") as file:
                # Now write the new/updated content
                file.seek(0)
                file.write(newContent)
            return True

        except Exception as e:
            authentication.logging.log(f"File read or write error", f"File: {self.path}, Error: {str(e)}", True)
            return False
        

    def _remove(self, id):
        """Remove a line from the file (by id)"""
    
        try:

            if not os.path.exists(self.path):
                # There is nothing to read
                return False
            with open(self.path, "r") as file:
                file.seek(0)
                content = file.read()
            content = content.strip("\n").split("\n")
            l = 0
            found = False
            newContent = ""

            for line in content:
                l += 1 # Line number 
                if found == True or (self.idField is None and l != id):
                    # Keep the content of this line if we've already found or have yet to reach the correct line number (only possible if there is no ID field)
                    newContent += line + "\n"
                    continue
                try:
                    # Try to decrypt line and parse as JSON
                    lineModel = json.loads(storage.encryption.decrypt(line))
                except:
                    # Invalid JSON or decryption failed
                    authentication.logging.log("Data parsing", "Raw data: " + str(line), True)
                    continue
                if self.idField is None or (self.idField in lineModel and lineModel[self.idField] == id):
                    # We've found it: remove (don't keep) this line and skip to the next
                    found = True
                    continue
                elif self.idField is not None and self.idField not in model:
                    # ID field unexpectedly not included in the validated model (configuration error)
                    authentication.logging.log(f"Validation error in {self.name}", f"Validated model does not contain ID field {self.idField}: {str(lineModel)}", True)
                # If we get here it's not yet found, keep this line as-is and try the next one
                newContent += line + "\n"
            
            if found == False:
                # The line to delete was not found
                return False
            
            if newContent.strip() == "" and os.path.exists(self.path):
                # There is no content left to be saved, remove the file because Python does not like reading empty files
                os.remove(self.path)
                return True
            
            with open(self.path, "w") as file:
                # Now write the new/updated content
                file.seek(0)
                file.write(newContent)
            return True

        except Exception as e:
            authentication.logging.log(f"Error reading or writing file", f"File: {self.path}, Error: {str(e)}", True)
            return False
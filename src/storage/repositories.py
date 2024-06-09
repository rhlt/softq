# Abstract storage repository (for user data that is stored on disk: Users, Members, Logs)

import data.forms
import auth.user
import auth.logging
import storage.encryption
import json

class Repository:
    """Abstract repository class"""

    def __init__(self):
        self.form = data.forms.Form()
        self.name = self.__class__.__name__

    def validate(self, action, model):
        """Validate form model and log all validation errors"""

        if self.form.validate(model):
            return True
        for field in self.form.errors:
            for error in self.form.errors[field]:
                auth.logging.log(f"Try to {action} invalid data in {self.name} (field: '{field}'): {error}", True)
        return False
    
    # Default roles (all "none" unless overwritten by subclasses)
    def canRead(self):
        return "none"
    def canInsert(self):
        return "none"
    def canUpdate(self):
        return "none"
    def canDelete(self):
        return "none"
    

class FileRepository(Repository):
    """Repository class that represents lines in a file"""

    def __init__(self, path):
        super().__init__()
        self.path = path

    def insert(self, model):
        """Insert a new line into a file"""

        if not auth.user.check_access(self.canInsert(), f"Unauthorized Insert call in {self.__class__.__name__}", True):
            return False # User has no access (and that is suspicious)
        
        if not self.validate("insert", model):
            return False # Form model is not valid
        
        line = storage.encryption.encrypt(json.dumps(model)) + "\n"
        open(self.path, "a").write(line)
    

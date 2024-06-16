import validation.forms
import authentication.user
import storage.abstract


class Members(storage.abstract.SQLiteRepository):
    """Users repository class"""

    def __init__(self, path = "./output/database"):
        super().__init__(path)
        self.form = validation.forms.Member() # User form with all fields
        self.idField = "id"
        self._initialize()
    
    def readRole(self, id, item):
        return "consult"
    def updateRole(self, id, item):
        return "consult"
    def deleteRole(self, id, item):
        return "admin" # Only admin can delete member
    def insertRole(self):
        return "consult"
    

class Users(storage.abstract.SQLiteRepository):
    """Users repository class"""

    def __init__(self, path = "./output/database"):
        super().__init__(path)
        self.form = validation.forms.User() # User form with all fields
        self.editForm = lambda item: validation.forms.User() if authentication.user.hasRole("super") else validation.forms.Consultant() if item["role"] == "CONSULTANT" else validation.forms.Administrator()
        self.idField = "username"
        self._initialize()
    
    def readRole(self, id, item):
        return "admin"
    def updateRole(self, id, item):
        return "consult" if authentication.user.name() == id else "admin" if item["role"].upper() == "CONSULTANT" else "super" # Users can edit their own profile
    def deleteRole(self, id, item):
        return "none" if authentication.user.name() == id else "admin" if item["role"].upper() == "CONSULTANT" else "super" # No one can delete their own profile
    def insertRole(self):
        return "admin" # Only admin can create new users
    
    def fieldCheck(self, field, model, value):
        """Check if the suggested value is permitted in the field (return the permitted value; anything other than the given value will be logged)"""
        if field == "role" and not authentication.user.hasRole("super"):
            return "Consultant" if model is None else model[field] # Do not allow changing the role field unless user is super admin
        return value
    

class Logs(storage.abstract.FileRepository):
    """Logs repository class (only used for reading because otherwise logging would cause circular references)"""

    def __init__(self, path = "./output/logs"):
        super().__init__(path)
        self.form = validation.forms.Log() # Log form with all fields
    
    def readRole(self, id, item):
        return "admin" # Overwrite 'read' access role
    

class SuspiciousLogs(storage.abstract.FileRepository):
    """Suspicious Logs repository class, for keeping track of unviewed suspicious logs (these are deleted when viewed, all logs are available in the Logs repository)"""

    def __init__(self, path = "./output/logs-suspicious"):
        super().__init__(path)
        self.form = validation.forms.Log() # Log form with all fields
    
    def readRole(self, id, item):
        return "admin" # Overwrite 'read' access role
    def deleteRole(self, id, item):
        return "admin" # Overwrite 'delete' access role (to "mark as read" means to delete from here; all logs will stay available in the Logs repository)
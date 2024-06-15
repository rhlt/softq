import validation.forms
import authentication.user
import storage.abstract


class Members(storage.abstract.FileRepository):
    """Users repository class"""

    def __init__(self):
        super().__init__("./output/members")
        self.form = validation.forms.Member() # User form with all fields
        self.idField = "id"
    
    def canRead(self, id):
        return "consult"
    def canUpdate(self, id):
        return "consult"
    def canDelete(self, id):
        return "admin" # Only admin can delete member
    def canInsert(self):
        return "consult"
    

class Users(storage.abstract.FileRepository):
    """Users repository class"""

    def __init__(self):
        super().__init__("./output/users")
        self.form = validation.forms.User() # User form with all fields
        self.idField = "username"
    
    def canRead(self, id):
        return "consult" if authentication.user.name() == id else "admin" # Consultant can read their own profile
    def canUpdate(self, id):
        return "consult" if authentication.user.name() == id else "admin" # Consultant can update their own profile
    def canDelete(self, id):
        return "none" if authentication.user.name() == id else "admin" # No one can delete their own profile
    def canInsert(self):
        return "admin" # Only admin can create new users
    

class Logs(storage.abstract.FileRepository):
    """Logs repository class (only used for reading because otherwise logging would cause circular references)"""

    def __init__(self):
        super().__init__("./output/logs")
        self.form = validation.forms.Log() # Log form with all fields
    
    def canRead(self, id):
        return "admin" # Overwrite 'read' access role
    

class SuspiciousLogs(storage.abstract.FileRepository):
    """Suspicious Logs repository class, for keeping track of unviewed suspicious logs (these are deleted when viewed, all logs are available in the Logs repository)"""

    def __init__(self):
        super().__init__("./output/logs-suspicious")
        self.form = validation.forms.Log() # Log form with all fields
    
    def canRead(self, id):
        return "admin" # Overwrite 'read' access role
    def canDelete(self, id):
        return "admin" # Overwrite 'delete' access role (to "mark as read" means to delete from here; all logs will stay available in the Logs repository)
import validation.forms
import storage.abstract


class Logs(storage.abstract.FileRepository):
    """Logs repository class (only used for reading because otherwise logging would cause circular references)"""

    def __init__(self):
        super().__init__("./output/.logs")
        self.form = validation.forms.Log() # Log form with all fields
    
    def canRead(self, id):
        return "admin" # Overwrite 'read' access role
    
    # FOR TESTING
    def canUpdate(self, id):
        return "admin"
    def canDelete(self, id):
        return "admin"
    def canInsert(self):
        return "admin"
    def canChange(self, id, newValues):
        return "admin" if "username" not in newValues else "none"
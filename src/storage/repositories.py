import data.forms
import storage.abstract


class Logs(storage.abstract.FileRepository):
    """Logs repository class (only used for reading because otherwise logging would cause circular references)"""

    def __init__(self):
        super().__init__("./output/.logs")
        self.form = data.forms.Log() # Log form with all fields
    
    def canRead(self, id):
        return "admin" # Overwrite 'read' access role
# Definitions of File repositories (Logs)

import storage.repositories
import data.forms


class Logs(storage.repositories.FileRepository):
    """Logs repository class (only used for reading because otherwise logging would cause circular references)"""

    def __init__(self):
        super().__init__("./output/.logs")
        self.form = data.forms.Log() # Link Log form with all fields
    
    def canRead(self):
        return "admin" # Overwrite 'read' access role
# Classes for different user roles


class Unauthorized:
    """Basic unauthorized user class, this does not allow the user any access (might not be logged in with password!)"""

    def __init__(self, name, model = None):
        """Initialize user object with username and data model"""
        self.name = name
        self.model = model
    
    def can(self, _):
        """Can't perform any actions"""
        return False
    
    def unauthorized(self):
        """See if the user is completely unauthorized (not correctly logged in)"""
        return self.__class__.__name__ == "Unauthorized"
    

class Consultant(Unauthorized):
    """Consultant class"""

    def can(self, role):
        """Consultant can 'consult' and 'password' (=change their own password)"""
        return super().can(role) or role == "consult" or role == "nothardcoded"


class Administrator(Consultant):
    """Administrator class"""

    def can(self, role):
        """Administrator can 'admin', 'consult' or 'password'"""
        return super().can(role) or role == "admin"


class SuperAdministrator(Administrator):
    """Super Administrator class"""

    def can(self, role):
        """Super Administrator can 'super', 'admin' or 'consult', but not 'nothardcoded' (since it is hard-coded)"""
        return role != "nothardcoded" and super().can(role) or role == "super"
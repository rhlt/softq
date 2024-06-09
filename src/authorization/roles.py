# Classes for different user roles


class Unauthorized:
    """Basic unauthorized user class, this does not allow the user any access (might not be logged in with password!)"""

    def __init__(self, name):
        """Initialize user object with username"""
        self.name = name
    
    def can(self, _):
        """Can't perform any actions"""
        return False
    

class Consultant(Unauthorized):
    """Consultant class"""

    def can(self, role):
        """Consultant can only 'consult'"""
        return super().can(role) or role == "consult"


class Administrator(Consultant):
    """Administrator class"""

    def can(self, role):
        """Administrator can 'admin' or 'consult'"""
        return super().can(role) or role == "admin"


class SuperAdministrator(Administrator):
    """Super Administrator class"""

    def can(self, role):
        """Super Administrator can 'super', 'admin' or 'consult'"""
        return super().can(role) or role == "super"
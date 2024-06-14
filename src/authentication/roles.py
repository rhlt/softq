# Classes for different user roles


class Unauthorized:
    """Basic unauthorized user class, this does not allow the user any access (might not be logged in with password!)"""

    def __init__(self, name):
        """Initialize user object with username"""
        self.name = name
    
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
        return super().can(role) or role == "consult" or role == "password"


class Administrator(Consultant):
    """Administrator class"""

    def can(self, role):
        """Administrator can 'admin', 'consult' or 'password'"""
        return super().can(role) or role == "admin"


class SuperAdministrator(Administrator):
    """Super Administrator class"""

    def can(self, role):
        """Super Administrator can 'super', 'admin' or 'consult', but not 'password' (since it is hard-coded)"""
        return role != "password" and super().can(role) or role == "super"
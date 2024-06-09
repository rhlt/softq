# Authorization classes

import authorization.roles
import data.forms

currentUser = None
try:
    maxAttempts = int(open(r".login-attempts", "r").read())
except:
    maxAttempts = 5

def name():
    """Get the current user name"""
    return currentUser.name if currentUser is not None else None

def login():
    """Let a user enter their username and password to log in"""
    global currentUser, maxAttempts
    
    if currentUser is None:
        # Mark current user as unauthorized (will ask for login)
        currentUser = authorization.roles.Unauthorized(None)
    
    while isinstance(currentUser, authorization.roles.Unauthorized) and maxAttempts > 0:
        # Ask for login details until user is no longer unauthorized

        print("Please log in:")    
        result = data.forms.Login().run()

        if result is None:
            # Canceled with Ctrl+C
            return False
        
        # Save the username we're trying to log in as
        currentUser.name = result["username"]

        if result["username"] == "super_admin":
            # Log in as super administrator
            if result["password"] == "Admin_123?":
                currentUser = authorization.roles.SuperAdministrator(result["username"])
        else:
            # TODO Find user by username
            pass

        if isinstance(currentUser, authorization.roles.Unauthorized):
            # Not logged in correctly
            print(" :: The username or password is incorrect")
            maxAttempts -= 1
            open(r".login-attempts", "w").write(str(maxAttempts))
        
    if maxAttempts <= 0:
        # Too many failed logins
        print("You have reached the maximum amount of login attempts.")
        return False

    return True


def check_access(role):
    """Check if current user has access to role"""
    global currentUser
    
    if not login():
        # Canceled login
        return False

    if isinstance(currentUser, authorization.roles.Unauthorized):
        print("You are now logged in as " + currentUser.name)

    if not currentUser.can(role):
        # LOG currentUser.name
        print("You are not allowed to perform this action. This incident will be reported.")
        return False

    return True


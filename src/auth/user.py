# Authorization classes

import auth.logging
import auth.roles
import data.forms

currentUser = None
try:
    maxAttempts = int(open(r"./output/.login-attempts", "r").read())
except:
    maxAttempts = 5

def name():
    """Get the current user name"""
    return currentUser.name if currentUser is not None else None

def logged_in():
    """Return if user is correctly logged in"""
    return currentUser is not None and not currentUser.unauthorized()

def login():
    """Let a user enter their username and password to log in"""
    global currentUser, maxAttempts
    
    if logged_in():
        # Already logged in
        return False
    
    # Mark current user as unauthorized (will ask for login)
    currentUser = auth.roles.Unauthorized(None)
    
    while currentUser.unauthorized() and maxAttempts > 0:
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
                currentUser = auth.roles.SuperAdministrator(result["username"])
        else:
            # TODO Find user by username
            pass

        if currentUser.unauthorized():
            # Not logged in correctly
            print(" :: The username or password is incorrect")
            auth.logging.log("Incorrect login")
            maxAttempts -= 1
            open(r"./output/.login-attempts", "w").write(str(maxAttempts))
        
    if maxAttempts <= 0:
        # Too many failed logins
        print("You have reached the maximum amount of login attempts.")
        auth.logging.log("Login blocked: reached maximum amount of login attempts", True)
        return False

    return True


def check_access(role, report, suspicious = False):
    """Check if current user has access to role"""
    global currentUser
    
    if not login():
        # Canceled login
        return False

    if not currentUser.unauthorized():
        print("You are now logged in as " + currentUser.name)

    if not currentUser.can(role):
        auth.logging.log(report, suspicious)
        print("You are not allowed to perform this action. This incident will be reported.")
        return False

    return True


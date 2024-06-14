# Authorization classes

import os
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

def loggedIn():
    """Return if user is correctly logged in"""
    return currentUser is not None and not currentUser.unauthorized()

def login():
    """Let a user enter their username and password to log in"""
    global currentUser, maxAttempts
    
    if loggedIn():
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

        if result["username"] == "super_admin" and result["password"] == "Admin_123?":
            # Log in as super administrator
            currentUser = auth.roles.SuperAdministrator(result["username"])
        else:
            # TODO Find user by username
            if result["username"] == "admin" and result["password"] == " ":
                # Log in as super administrator
                currentUser = auth.roles.Administrator("TEST ADMIN")
            elif result["username"] == " " and result["password"] == " ":
                currentUser = auth.roles.Consultant("TEST CONSULTANT")

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


    auth.logging.log("Logged in")
    try:
        # Reset login attempts
        os.remove(r"./output/.login-attempts")
    except:
        # Not a problem if file does not exist because there have been no incorrect login attempts
        pass
    return True


def hasAccess(role):
    """Check if current user has access to role"""
    global currentUser

    if currentUser is None:
        return False
    if currentUser.unauthorized():
        return False
    
    return currentUser.can(role)    


def requireAccess(role, reportMessage, suspicious = False):
    """Check if current user has access to role, allow them to log in if they aren't yet, and report them if they are unauthorized"""
    global currentUser
    
    if not login():
        # Login was canceled
        return False

    if not currentUser.unauthorized():
        print("You are logged in as " + currentUser.name)

    if not hasAccess(role):
        auth.logging.log(reportMessage, suspicious)
        print("You are not allowed to perform this action. This incident will be reported.")
        return False

    return True


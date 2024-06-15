# Authorization classes

import os
import authentication.logging
import authentication.roles
import storage.repositories
import validation.forms

currentUser = None
try:
    with open(r"./output/login-attempts", "r") as file:
        maxAttempts = int(file.read())
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
    currentUser = authentication.roles.Unauthorized(None)
    
    while currentUser.unauthorized() and maxAttempts > 0:
        # Ask for login details until user is no longer unauthorized

        print("Please log in:")    
        result = validation.forms.Login().run()
        usersRepository = storage.repositories.Users()

        if result is None:
            # Canceled with Ctrl+C
            return False
        
        # Save the username we're trying to log in as
        currentUser.name = result["username"]

        foundUser = None
        foundAdmin = None
        if result["username"] == "super_admin" and result["password"] == "Admin_123?":
            # Log in as super administrator
            currentUser = authentication.roles.SuperAdministrator(result["username"])
        else:
            # Find the user in the Users repository
            foundUser = usersRepository._one(currentUser.name)
            print("FOUND USER", foundUser)
            foundAdmin = foundUser is not None and foundUser["admin"].upper() == "Y"

            if result["username"] == "admin" and result["password"] == " ":
                # Log in as super administrator
                currentUser = authentication.roles.Administrator(currentUser.name)
            elif result["username"] == " " and result["password"] == " ":
                currentUser = authentication.roles.Consultant(currentUser.name)

        if currentUser.unauthorized():
            # Not logged in correctly
            print(" :: The username or password is incorrect")
            if foundUser is None:
                logDetail = f"{currentUser.name} is not an existing user"
            elif foundAdmin:
                logDetail = f"{currentUser.name} is an administrator"
            else:
                logDetail = f"{currentUser.name} is a consultant"
            authentication.logging.log("Incorrect login", logDetail)
            maxAttempts -= 1
            with open(r"./output/login-attempts", "w") as file:
                file.write(str(maxAttempts))
        
    if maxAttempts <= 0:
        # Too many failed logins
        print("You have reached the maximum number of login attempts.")
        authentication.logging.log("Login blocked", "Reached maximum allowed number of login attempts", True)
        return False


    authentication.logging.log("Logged in", "Role: " + currentUser.__class__.__name__)
    try:
        # Reset login attempts
        os.remove(r"./output/login-attempts")
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


def requireAccess(role, activity, details, suspicious = False):
    """Check if current user has access to role, allow them to log in if they aren't yet, and report them if they are unauthorized"""
    global currentUser
    
    if currentUser is None and not login():
        # Login was canceled
        return False

    if not hasAccess(role):
        authentication.logging.log(activity, details, suspicious)
        print("You are not allowed to perform this action. This incident will be reported.")
        return False

    return True


# Authorization classes

import os
import authentication.logging
import authentication.roles
import storage.encryption
import storage.repositories
import validation.fields
import validation.rules
import validation.forms

# Initialization
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


def role():
    """Get the current role if the user is logged in"""
    return currentUser.role if loggedIn() else None


def model():
    """Return the user model (profile fields) if the user is logged in"""
    return currentUser.model if loggedIn() else None


def checkPassword(password, user = None):
    """Check if the password is correct for the current or given user"""
    if user is None:
        user = model()
    if user is None:
        return False
    return storage.encryption.checkDataHash(password, user["password"])


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
        ### if result["username"] == "super_admin" and result["password"] == "Admin_123?":
        if result["username"] == "admin" and result["password"] == " ":
            # Log in as super administrator
            currentUser = authentication.roles.SuperAdministrator(result["username"])
        else:
            # Find the user in the Users repository
            foundUser = usersRepository.readInternal(currentUser.name, False)
            if foundUser is not None:
                foundAdmin = foundUser["role"].upper() == "ADMINISTRATOR"
                currentUser.model = foundUser
                if checkPassword(result["password"], foundUser):
                    # Password is correct, create the correct User class
                    if foundAdmin:
                        currentUser = authentication.roles.Administrator(currentUser.model["username"], currentUser.model)
                    else:
                        currentUser = authentication.roles.Consultant(currentUser.model["username"], currentUser.model)
                    if not validation.fields.Text("Login password", validation.rules.passwordRules).validate(result["password"], False, False):
                        # Password does not conform to current password rules, require user to set a new one (except hard-coded users)
                        if currentUser.can("nothardcoded") and not changePassword(result["password"]):
                            # Canceled: force log out
                            return False

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
        print("You have reached the maximum number of login attempts. (Delete the 'login-attempts' file in the output folder to bypass this)")
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


def changePassword(currentPassword = None):
    """Let a user change their password"""
    global currentUser

    if not loggedIn():
        return

    if currentPassword is None:
        print("Change your password")
        print("*" * len("Change your password"))    
        # User will be asked for current password first
        result = validation.forms.ChangePassword().run()
    else:
        # Automatically fill in current password if we came here immediately after login
        print("Your password has expired. Please choose a new password:")
        result = validation.forms.ChangePassword().run({ "currentPassword": currentPassword }, ["currentPassword"])

    if result is None:
        return # Canceled
    
    repository = storage.repositories.Users()
    if currentUser.model is None or not authentication.user.checkPassword(result["currentPassword"]):
        authentication.logging.log("Change password failed", f"Incorrect current password entered.")
        print(":: The current password is not correct")
    elif currentUser.model is not None:
        # Replace the password hash in the user model
        currentUser.model["password"] = storage.encryption.hashDataWithSalt(result["newPassword"])
        if repository.update(currentUser.name, currentUser.model):
            # Update was successful
            authentication.logging.log("Password changed", f"User has manually changed password")
            print(f"Your password has been changed")
        else:
            # Update was not successful (?)
            print(f"Failed to change your password (please check the logs)")
    validation.fields.EmptyValue(f"Press enter to continue").run()
    return True


def hasRole(role):
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

    if not hasRole(role):
        authentication.logging.log(activity, details, suspicious)
        print("You are not allowed to perform this action. This incident will be reported.")
        return False

    return True


# Logic for actions that fall outside the menus and repository table view

import validation.fields
import validation.forms
import authentication.user
import authentication.logging
import storage.encryption
import storage.repositories


def changePassword(currentPassword = None):
    """Allow current user to change their password"""

    print() # newline
    if not authentication.user.requireAccess("nothardcoded", "Change password", "Illegal attempt to change own password", True):
        return
    authentication.user.changePassword()


def createNewItem(title, repository, fixedValues = None, runAfter = lambda _: None):
    """Create a new item in a repository, with default values available"""

    print() # newline
    print(title)
    print("*" * len(title))

    print("Please complete all fields or press Ctrl+C to cancel")

    if fixedValues is None:
        fixedValues = {}
    
    model = repository.form.run(fixedValues, fixedValues.keys())
    if model is None:
        return # Canceled
    
    # Allow some last changes to be made
    runAfter(model)
    
    if repository.idField is not None and repository.idField in model and repository._one(model[repository.idField]) is not None:
        # Item with this ID already exists!
        print(f"{repository.form.name} with {repository.form.fields[repository.idField].name} '{model[repository.idField]}' already exists!")
    elif repository.insert(model):
        # Insertion was successful
        print(f"{repository.form.name} added successfully")
    else:
        # Insertion was not successful (?)
        print(f"Failed to add {repository.form.name} (please check the logs)")
    validation.fields.EmptyValue(f"Press enter to go back").run()


def searchItem(title, repositoryMenu):
    """Search an item in a repository menu"""
    
    print() # newline
    print(title)
    print("*" * len(title))

    search = validation.fields.Text(f"Search term").run()
    if search is None:
        return
    
    repositoryMenu.search = search
    return repositoryMenu.run()


def hashGeneratedPassword(model):
    """Hash a generated model password"""
    password = model["password"]
    print("Generated a temporary password: " + password)
    authentication.logging.log("Generated temporary password", f"User: {model['username']}")
    model["password"] = storage.encryption.hashDataWithSalt(password)


def resetPassword(id, model):
    """Reset a user's password (generates a temporary password)"""
    result = validation.fields.Text(f"Are you sure you want to reset the password for {model['username']}? (Y/N)", [validation.rules.valueInList(["Y", "N"])]).run()
    if result is None or result.upper() != "Y":
        return
    model["password"] = storage.encryption.tempPassword()
    hashGeneratedPassword(model) # Hashes newly generated password and shows it on screen
    repository = storage.repositories.Users()
    if repository.update(id, model):
        # Update was successful
        print(f"The password has been reset")
    else:
        # Update was not successful (?)
        print(f"Failed to reset the password (please check the logs)")
    validation.fields.EmptyValue(f"Press enter to continue").run()
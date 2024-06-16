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
    username = authentication.user.name()
    model = authentication.user.model()
    if model is None or not authentication.user.checkPassword(result["currentPassword"]):
        print("# INCORRECT PASSWORD ON CHANGE", model, result["currentPassword"])
        print(":: The current password is not correct")
    elif model is not None:
        # Replace the password hash in the user model
        model["password"] = storage.encryption.hashDataWithSalt(result["newPassword"])
        if repository.update(username, model):
            # Update was successful
            print(f"Your password has been changed")
        else:
            # Update was not successful (?)
            print(f"Failed to change your password (please check the logs)")
    validation.fields.EmptyValue(f"Press enter to continue").run()


def createNewItem(title, repository, fixedValues = None, runAfter = lambda _: None):
    """Create a new item in a repository, with default values available"""

    print() # newline
    print(title)
    print("*" * len(title))

    print("Please complete all fields or press Ctrl+C to cancel")

    if fixedValues is None:
        fixedValues = {}
    
    model = repository.form.run(fixedValues, fixedValues.keys())
    print("## MODEL", model)

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
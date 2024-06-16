# Logic for actions that fall outside the menus and repository table view

import validation.fields
import validation.forms
import authentication.user
import authentication.logging


def changePassword():
    """Allow current user to change their password"""

    print() # newline
    print("Change your password")
    print("*" * len("Change your password"))
    
    if not authentication.user.requireAccess("nothardcoded", "Change password", "Illegal attempt to change own password", True):
        return
    
    result = validation.forms.ChangePassword().run()
    if result is None:
        return # Canceled
    
    print("## CHANGE PASSWORD", result)


def createNewItem(title, repository, fixedValues = None):
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
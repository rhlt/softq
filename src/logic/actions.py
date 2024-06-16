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


def createNewItem(title, repository, defaults = None):
    """Create a new item in a repository, with default values available"""

    print() # newline
    print(title)
    print("*" * len(title))

    print("Please complete all fields or press Ctrl+C to cancel")
    
    model = repository.form.run(defaults)    
    print("## MODEL", model)

    if model is None:
        return # Canceled

    if repository.insert(model):
        validation.fields.EmptyValue(f"{repository.form.name} added successfully").run()
    else:
        validation.fields.EmptyValue(f"Failed to add {repository.form.name}").run()
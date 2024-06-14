# Logic to change user information

import validation.forms
import validation.fields

def changePassword():
    # Let user change password

    print("Change your password (press Ctrl+C to cancel):")

    form = validation.forms.ChangePassword()
    result = form.run()
    if result is None:
        return
    
    # TODO check and save new password

    print(result)
    print("Your password has been changed or something")

    validation.fields.EmptyValue("Press Enter to return to the main menu").run()
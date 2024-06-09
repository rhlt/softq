# Logic to change user information

import data.forms

def change_password():
    # Let user change password

    print("Change your password (press Ctrl+C to cancel):")

    form = data.forms.ChangePassword()
    result = form.run()
    if result is None:
        return
    
    # TODO check and save new password

    print(result)
    
    
    

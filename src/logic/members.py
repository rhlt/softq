# Logic to change member profiles

import validation.forms
import authentication.user

def addMember():
    # Let user change password

    print("Add new member (press Ctrl+C to cancel):")

    form = validation.forms.Member()
    result = form.run()
    if result is None:
        return
    
    # TODO check and save member data

    print(result)
    
    
    

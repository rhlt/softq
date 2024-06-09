# Logic to change member profiles

import data.forms

def add_member():
    # Let user change password

    print("Add new member (press Ctrl+C to cancel):")

    form = data.forms.Member()
    result = form.run()
    if result is None:
        return
    
    # TODO check and save member data

    print(result)
    
    
    

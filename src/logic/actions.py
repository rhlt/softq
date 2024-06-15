# Logic for actions that fall outside the menus and repository table view

import validation.fields

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
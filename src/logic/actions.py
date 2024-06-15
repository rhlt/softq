# Logic for actions that fall outside the repository table view

def createNewItem(title, repository):
    """Create a new item in a repository"""
    print() # newline
    print(title)
    print("*" * len(title))

    model = repository.form.run()
    if model is None:
        return
    
    print("## CREATE", model)

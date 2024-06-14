# Logic to display interfaces

import validation.fields
import authentication.user

class Menu:
    """Menu class that displays a menu of options and asks the user to input a number to choose a menu option"""

    def __init__(self, title, options):
        self.title = title
        self.options = options
        self.description = f"Please enter an option (1-{len(self.options)}):"
        self.fieldName = "Option"


    def run(self):
        print() # newline
        print(self.title)
        print("*" * len(self.title))

        if not authentication.user.loggedIn():
            authentication.user.login()
            
        print(self.description)
        if isinstance(self.options, list):
            self.options = dict(zip([str(n) for n in range(1, len(self.options) + 1)], self.options)) # List to dictionary with numbered keys ("1", "2", "3", ...)
        optionsAvailable = False
        for option in self.options:
            if self.options[option].role is not None and not authentication.user.hasAccess(self.options[option].role):
                # Only show menu items the user is supposed to see
                continue
            optionsAvailable = True
            print(f"  {option}: {self.options[option].title}")

        if optionsAvailable:
            # Generate a field from the list of options
            optionField = validation.fields.FromList(self.fieldName, list(self.options) + [""])
        else:
            # There are no options, or none are accessible to the current user
            optionField = validation.fields.EmptyValue("There is no data to be shown")

        # Receive user input
        choice = optionField.run()
        if choice is None:
            return # Always cancel in case no options are available or user pressed Ctrl+C
        
        print() # newline

        if len(choice) > 0:
            # Run the chosen action
            cancel = self.options[choice].action()
        else:
            cancel = self.noInput()
        if cancel is None and not optionsAvailable or cancel:
            return

        while choice is not None:
            choice = self.run() # Keep running the menu until canceled with Ctrl+C

    def noInput(self):
        """What happens when the user presses enter without any input: if this returns True, the menu is canceled, if False the menu is run again"""
        pass


class RepositoryMenu(Menu):
    """Class that lists items in the repository"""

    def __init__(self, title, repository):
        """Initialize by generating menu option from repository items"""
        self.offset = 0
        self.limit = 20
        self.repository = repository
        self.title = title
        self.fieldLabel = "Line number" if repository.idField is None else repository.idField
        self.fieldName = f"{self.fieldLabel} (leave empty to show next page)"
        self.description = ""
        self.generateOptions()


    def generateOptions(self):
        """Generate items"""
        items = self.repository.readAll(self.offset, self.limit)
        if items is None or len(items) == 0:
            self.options = {}
            self.description = "You've reached the end of the data. Press enter to view the first page or press Ctrl+C to cancel" if self.offset > 0 else ""
            return
        menuOptions = map(lambda id: MenuOption(str(items[id]), lambda: self.viewItem(id), self.repository.canRead(id)), items)
        self.options = dict(zip([str(id) for id in items.keys()], menuOptions))
        self.description = f"Showing items {self.offset+1}-{self.offset+self.limit}\nPlease enter a {self.fieldLabel} to view or press Ctrl+C to cancel"

    
    def viewItem(self, id):
        """View the item that was selected"""
        item = self.repository.readOne(id)
        self.repository.form.display(item)


    def noInput(self):
        """No input: prepare the next page (or loop back to the first page if we've reached the end)"""
        if len(self.options) > 0:
            self.offset += self.limit
        else:
            if self.offset == 0:
                return True # Prevent getting "stuck" in screen that is completely empty
            self.offset = 0
        self.generateOptions()
        return False



class MenuOption:
    """Menu option class"""

    def __init__(self, title, action, role = None):
        self.title = title
        self.action = action
        self.role = role # required role to see the menu item (None = anyone)
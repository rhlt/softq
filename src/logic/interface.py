# Logic to display interfaces

import validation.fields
import authentication.user

class MenuOption:
    """Simple class that represents a menu option"""

    def __init__(self, title, action, role = None):
        self.title = title
        self.action = action # action (lambda) to be executed when this menu option is chosen
        self.role = role # required role to see the menu item (None = anyone)


class Menu:
    """Menu class that displays a menu of options and asks the user to input a number to choose a menu option"""

    def __init__(self, title, options, extraAction = None):
        self.title = title
        self.options = options
        self.description = f"Please enter an option number or press Ctrl+C to cancel:"
        self.fieldName = "Option"
        self.extraAction = extraAction
        self.optionSeparator = ": "


    def run(self):
        """Show the menu"""
        print() # newline
        print(self.title)
        print("*" * len(self.title))

        if not authentication.user.loggedIn() and not authentication.user.login():
            return # Not login and login was canceled

        if self.extraAction is not None:
            self.extraAction()
            
        print(self.description)

        if isinstance(self.options, list):
            self.options = dict(zip([str(n) for n in range(1, len(self.options) + 1)], self.options)) # List to dictionary with numbered keys ("1", "2", "3", ...)
        optionsAvailable = []
        optionLength = 0
        for option in self.options:
            if self.options[option].role is not None and not authentication.user.hasRole(self.options[option].role):
                # Only show menu items the user is supposed to see
                continue
            optionLength = len(option) if optionLength < len(option) else optionLength
            optionsAvailable.append(option)

        if len(optionsAvailable) > 0:
            # Generate a field from the list of options
            optionField = validation.fields.FromList(self.fieldName, optionsAvailable + [""])
            for option in optionsAvailable:
                print(f"  {option.ljust(optionLength)}{self.optionSeparator}{self.options[option].title}")
            print() # newline
        else:
            # There are no options, or none are accessible to the current user
            optionField = validation.fields.EmptyValue("Press enter to go back")

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

    def __init__(self, title, repository, deleteWhenViewed = False):
        """Initialize by generating menu option from repository items"""
        self.repository = repository
        self.title = title
        self.fieldLabel = "Line number" if repository.idField is None else repository.form.fields[repository.idField].name
        self.fieldName = f"{self.fieldLabel} (leave empty to show next page)"
        self.description = ""
        self.offset = 0
        self.limit = 20
        self.deleteWhenViewed = deleteWhenViewed # Repositories that need to be deleted when viewed
        self.extraAction = None
        self.optionSeparator = " | "


    def run(self):
        """Load the options and show the menu"""
        self.generateOptions()
        super().run()


    def generateOptions(self):
        """Generate menu options for items"""
        items = self.repository.readAll(self.offset, self.limit)
        if items is None or len(items) == 0:
            self.options = {}
            self.description = "You've reached the end of the data. Press enter to view the first page or press Ctrl+C to cancel" if self.offset > 0 else "There is nothing to display"
            return


        menuOptions = map(lambda id: MenuOption(self.repository.form.row(items[id]), lambda: self.viewItem(id), self.repository.readRole(id, items[id])), items)
        self.options = dict(zip([str(id) for id in items.keys()], menuOptions))
        self.description = f"Showing items {self.offset+1}-{self.offset+self.limit}\nPlease type the {self.fieldLabel} to view or press Ctrl+C to cancel"
        padding = max(len(str(s)) for s in items.keys())
        idLabel = "  " + ("#" if self.repository.idField is None else self.fieldLabel).ljust(padding)[:padding]
        self.description += "\n\n" + self.repository.form.generateHeader(idLabel)

    
    def viewItem(self, id):
        """View the item that was selected"""
        RepositoryItem(f"{self.repository.form.name}: {id}", self.repository, id, self.deleteWhenViewed).run()


    def noInput(self):
        """No input: prepare the next page (or loop back to the first page if we've reached the end)"""
        if len(self.options) > 0:
            self.offset += self.limit
        else:
            if self.offset == 0:
                return True # Prevent getting "stuck" in a screen that is completely empty
            self.offset = 0
        return False
    

class RepositoryItem(Menu):
    """Class that shows an item in the repository and allows the user to select an action"""

    def __init__(self, title, repository, id, deleteWhenViewed = False):
        """Initialize by generating menu option from repository items"""
        self.id = id
        self.item = None
        self.repository = repository
        self.label = self.repository.form.name
        self.title = title
        self.description = f"Please select an action to perform or press Ctrl+C to cancel"
        self.fieldName = "Action"
        self.deleteWhenViewed = deleteWhenViewed
        self.extraAction = lambda: self.repository.form.display(self.item)
        self.optionSeparator = ": "

    
    def updateItem(self):
        """Helper function to update an item"""
        if self.item is None:
            # Item does not exist (anymore)
            validation.fields.EmptyValue(f"The {self.label} {self.id} does not exist").run()
            return True # Close RepositoryItem
        print() # newline
        print(f"Edit {self.label} {self.id}")
        print("*" * len(f"Edit {self.label} {self.id}"))
        print("Please enter the updated values. Leave values empty to keep the originals:")
        model = self.repository.form.run(self.item, [self.repository.idField])
        self.repository.update(self.id, model)
        return False # Return to (updated) RepositoryItem


    def deleteItem(self):
        """Helper function to delete an item"""
        if self.item is None:
            # Item does not exist (anymore)
            validation.fields.EmptyValue(f"The {self.label} {self.id} does not exist").run()
            return True # Close RepositoryItem
        print() # newline
        print(f"Delete {self.label} {self.id}")
        print("*" * len(f"Delete {self.label} {self.id}"))
        result = validation.fields.Text(f"Are you sure you want to delete {self.label} {self.id}? (Y/N)", [validation.rules.valueInList(["Y", "N"])]).run()
        if result is not None and result.upper() == "Y":
            if self.repository.delete(self.id):
                validation.fields.EmptyValue(f"{self.label} {self.id} was deleted").run()
                return True # Close RepositoryItem


    def generateOptions(self):
        """Generate menu options for the item"""
        self.item = self.repository.readOne(self.id)
        if self.item is None:
            self.options = {}
            return
        if not self.deleteWhenViewed:
            self.options = [
                MenuOption(f"Return to {self.label} list", lambda: True),
                MenuOption(f"Edit {self.label} {self.id}", self.updateItem, self.repository.updateRole(self.id, self.item)),
                MenuOption(f"Delete {self.label} {self.id}", self.deleteItem, self.repository.deleteRole(self.id, self.item)),
            ]
        else:
            self.options = [
                MenuOption(f"Mark as viewed", lambda: self.repository.delete(self.id), self.repository.deleteRole(self.id, self.item)),
                MenuOption(f"Return without marking as viewed", lambda: True),
            ]

    
    def run(self):
        """Run the menu and display the item"""
        self.generateOptions()
        super().run()

# Logic to display interfaces

import data.fields
import auth.user

class Menu:
    """Base menu class that displays a menu of options and asks the user to input a number to choose a menu option"""

    def __init__(self, title, options):
        self.title = title
        self.options = options

    def run(self):

        print() # newline
        print(self.title)
        print("*" * len(self.title))

        if not auth.user.loggedIn():
            auth.user.login()
            
        print(f"Please enter an option (1-{len(self.options)}):")
        i = 1
        optionNumbers = [""]
        for option in self.options:
            # TODO skip if not authorized
            optionNumbers.append(str(i))
            print(f"  {i}. {option.title}")
            i += 1
        
        # Receive user input
        optionField = data.fields.FromList("Option", optionNumbers)
        choice = optionField.run()
        if choice is None:
            return
        
        print() # newline

        if len(choice) > 0:
            # Run the chosen action
            cancel = self.options[int(choice) - 1].action()
        else:
            cancel = self.noInput()
        if cancel:
            return

        while choice is not None:
            choice = self.run() # Keep running the menu until canceled with Ctrl+C

    def noInput(self):
        """What happens when the user presses enter without any input: if this returns True, the menu is canceled, if False the menu is run again"""
        pass


class MenuOption:
    """Menu option class"""

    def __init__(self, title, action):
        self.title = title
        self.action = action
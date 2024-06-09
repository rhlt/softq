# Logic to display interfaces

import data.input
import authorization.user

class Menu:
    """Base menu class that displays a menu of options and asks the user to input a number to choose a menu option"""

    def __init__(self, title, options, access):
        self.title = title
        self.options = options
        self.access = access

    def run(self):

        print() # newline
        print(self.title)
        print("*" * len(self.title))

        if not authorization.user.check_access(self.access):
            # No access to this part of the system
            return None
        
        print(f"Please enter an option (1-{len(self.options)}):")
        i = 1
        option_numbers = [""]
        for option in self.options:
            # TODO skip if not authorized
            option_numbers.append(str(i))
            print(f"  {i}. {option.title}")
            i += 1
        
        # Receive user input
        option_input = data.input.FromList("Option", option_numbers)
        choice = option_input.run()
        if choice is None:
            return
        
        print() # newline

        if len(choice) > 0:
            # Run the chosen action
            cancel = self.options[int(choice) - 1].action()
        else:
            cancel = self.no_input()
        if cancel:
            return

        while choice is not None:
            choice = self.run() # Keep running the menu until canceled with Ctrl+C

    def no_input(self):
        """What happens when the user presses enter without any input"""
        pass


class MenuOption:
    """Menu option class"""

    def __init__(self, title, action):
        self.title = title
        self.action = action
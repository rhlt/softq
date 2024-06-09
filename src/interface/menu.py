# Display menu interfaces

import data.input
import interface.members
import interface.users

class Menu:
    """Base menu class that displays a menu of options and asks the user to input a number to choose a menu option"""

    def __init__(self, title, options):
        self.title = title
        self.options = options

    def run(self):

        print() # newline
        print(self.title)
        print("*" * len(self.title))
        print(f"Please enter an option (1-{len(self.options)}):")
        i = 1
        option_numbers = []
        for option in self.options:
            # TODO skip if not authorized
            option_numbers.append(str(i))
            print(f"- {i}. {option.title}")
            i += 1
        
        # Receive user input
        option_input = data.input.FromList("Option", option_numbers)
        choice = option_input.run()
        if choice is None:
            return
        
        print() # newline

        # Run the chosen action
        cancel = self.options[int(choice) - 1].action()
        if cancel:
            return
        
        while choice is not None:
            choice = self.run() # Keep running the main menu until canceled with Ctrl+C


class MenuOption:
    """Menu option class"""

    def __init__(self, title, action):
        self.title = title
        self.action = action

# Main menu options
main = Menu("Welcome to the Member Management System", [
    MenuOption("Display list of members", lambda: print("\nLIST MEMBERS")), # TODO AUTHORIZATION
    MenuOption("Search members", lambda: print("\nSEARCH MEMBERS")), # TODO AUTHORIZATION
    MenuOption("Add new member", interface.members.add_member), # TODO AUTHORIZATION
    MenuOption("Change your password", interface.users.change_password), # TODO AUTHORIZATION
    MenuOption("Log out (quit program)", lambda: True),
])
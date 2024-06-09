# The main menu; the entry point into the application

from logic.interface import Menu, MenuOption
import logic.users
import logic.members

# Main menu options
main = Menu("Welcome to the Member Management System", [
    MenuOption("Change your password", logic.users.change_password),
    MenuOption("List users and roles", lambda: None),
    MenuOption("Create new user", lambda: None),
    #MenuOption("Modify user", lambda: None),
    #MenuOption("Delete user", lambda: None),
    #MenuOption("Reset user password", lambda: None),
    MenuOption("Search members", logic.members.add_member),
    MenuOption("Add new member", lambda: None),
    #MenuOption("Modify member", lambda: None),
    #MenuOption("Delete member", lambda: None),
    MenuOption("Backup or Restore", lambda: None),
    MenuOption("Log out (quit program)", lambda: True),
])
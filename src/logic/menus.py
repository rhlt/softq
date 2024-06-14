# The main menu; the entry point into the application

from logic.interface import Menu, MenuOption, RepositoryMenu
import authentication.user
import logic.users
import logic.members
import storage.repositories

# Initialize the repositories
logsRepository = storage.repositories.Logs()

# Main menu options
main = Menu("Welcome to the Member Management System", [
    MenuOption("Change your password", logic.users.changePassword, "password"),
    MenuOption("List users and roles", lambda: None),
    MenuOption("Create a new user", lambda: None),
    MenuOption("Search members", logic.members.addMember),
    MenuOption("Add new member", lambda: None),
    MenuOption("Backup or Restore", lambda: None),
    MenuOption("View system logs", lambda: repositoryMenu("View system logs", logsRepository).run(), logsRepository.canRead(None)),
    MenuOption("Create new log", lambda: repositoryInsert("Create new log", logsRepository).run(), logsRepository.canInsert()),
    MenuOption("Log out (quit program)", lambda: True),
], lambda: authentication.user.loggedIn() and print("You are logged in as", authentication.user.name(), "\n"))

# Function to generate a repository menu interface
repositoryMenu = lambda title, repository: RepositoryMenu(title, repository)
repositoryInsert = lambda title, repository: None
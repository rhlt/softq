# The main menu; the entry point into the application

from logic.interface import Menu, MenuOption, RepositoryMenu
from logic.actions import changePassword, createNewItem
import authentication.user
import storage.encryption
import storage.repositories
import validation.datetime

# Initialize the repositories
membersRepository = storage.repositories.Members()
usersRepository = storage.repositories.Users()
logsRepository = storage.repositories.Logs()
suspiciousLogsRepository = storage.repositories.SuspiciousLogs()

def mainMenuAction():
    """Action performed whenever the main menu is shown"""
    if not authentication.user.loggedIn():
        return
    print("You are logged in as", authentication.user.name())
    if suspiciousLogsRepository.canRead(None):
        suspiciousActivities = suspiciousLogsRepository._list(0, 10)
        suspiciousNumber = len(suspiciousActivities)
        if suspiciousNumber == 10:
            # We won't load more than 10
            suspiciousNumber = "10 or more"
        if suspiciousNumber:
            print(f"There {'is' if suspiciousNumber == 1 else 'are'} {suspiciousNumber} unviewed suspicious {'activity' if suspiciousNumber == 1 else 'activities'} in the logs!")
    print() # newline

# Main menu options
main = Menu("Welcome to the Member Management System", [
    MenuOption("Change your password", changePassword, "nothardcoded"),
    MenuOption("Add new member", lambda: repositoryInsert("Add new member", membersRepository, { "registrationDate": validation.datetime.date() }), membersRepository.canInsert()),
    MenuOption("Search for a member", lambda: repositoryMenu("Search members", membersRepository).run(), membersRepository.canRead(None)),
    MenuOption("View all members", lambda: repositoryMenu("View all members", membersRepository).run(), membersRepository.canRead(None)),
    MenuOption("List users and roles", lambda: repositoryMenu("User overview", usersRepository).run(), usersRepository.canRead(None)),
    MenuOption("Create a new user", lambda: repositoryInsert("Create a new user", usersRepository, { "password": storage.encryption.tempPassword() }), usersRepository.canInsert()),
    MenuOption("Backup or Restore", lambda: print("NOT IMPLEMENTED")),
    MenuOption("View system logs", lambda: repositoryMenu("View system logs", logsRepository).run(), logsRepository.canRead(None)),
    MenuOption("View new suspicious logs", lambda: repositoryMenu("View new suspicious logs", suspiciousLogsRepository, True).run(), suspiciousLogsRepository.canRead(None)),
    MenuOption("Log out (quit application)", lambda: True),
], mainMenuAction)

# Lambdas to generate a repository menu interface
repositoryMenu = lambda title, repository, deleteWhenViewed = False: RepositoryMenu(title, repository, deleteWhenViewed)
repositoryInsert = lambda title, repository, defaults = None: createNewItem(title, repository, defaults)
# The main menu; the entry point into the application

from logic.interface import Menu, MenuOption, RepositoryMenu
from logic.actions import searchItem, createNewItem, changePassword, hashGeneratedPassword, resetPassword
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
    print(f"You are logged in as {authentication.user.name()} ({authentication.user.role()})")
    if authentication.user.hasRole(suspiciousLogsRepository.readRole(None, None)):
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
    MenuOption("Manage Users", lambda: users.run(), "admin"),
    MenuOption("Manage Members", lambda: members.run(), "consult"),
    MenuOption("System Maintanance", lambda: system.run(), "admin"),
    MenuOption("Log out (quit application)", lambda: True),
], mainMenuAction)

# Users menu options
users = Menu("Manage Users", [
    MenuOption("List users and roles", lambda: repositoryMenu("User overview", usersRepository, False, resetUserPassword), usersRepository.readRole(None, None)),
    MenuOption("Search users", lambda: repositorySearch("Search users", usersRepository, False, resetUserPassword), usersRepository.readRole(None, None)),
    MenuOption("Create a new consultant", lambda: repositoryInsert("Create a new consultant", usersRepository, { "registrationDate": validation.datetime.date(), "password": storage.encryption.tempPassword(), "role": "Consultant" }, hashGeneratedPassword), usersRepository.insertRole()),
    MenuOption("Create a new administrator", lambda: repositoryInsert("Create a new administrator", usersRepository, { "registrationDate": validation.datetime.date(),"password": storage.encryption.tempPassword(), "role": "Administrator" }, hashGeneratedPassword), "super"),
    MenuOption("Back to Main Menu", lambda: True),
])

# Members menu options
members = Menu("Manage Members", [
    MenuOption("Add new member", lambda: repositoryInsert("Add new member", membersRepository, { "registrationDate": validation.datetime.date() }), membersRepository.insertRole()),
    MenuOption("Search members", lambda: repositorySearch("Search members", membersRepository), membersRepository.readRole(None, None)),
    MenuOption("View all members", lambda: repositoryMenu("View all members", membersRepository), membersRepository.readRole(None, None)),
    MenuOption("Back to Main Menu", lambda: True),
])

# System menu options
system = Menu("System Maintenance", [
    MenuOption("Backup or Restore", lambda: print("## NOT IMPLEMENTED"), "super"),
    MenuOption("View system logs", lambda: repositoryMenu("View system logs", logsRepository), logsRepository.readRole(None, None)),
    MenuOption("View new suspicious logs", lambda: repositoryMenu("View new suspicious logs", suspiciousLogsRepository, True), suspiciousLogsRepository.readRole(None, None)),
    MenuOption("Search the logs", lambda: repositorySearch("Search the logs", logsRepository), logsRepository.readRole(None, None)),
    MenuOption("Back to Main Menu", lambda: True),
])

# Lambdas to generate a repository menu interface
repositoryMenu = lambda title, repository, deleteWhenViewed = False, extraItemOptions = None: RepositoryMenu(title, repository, deleteWhenViewed, extraItemOptions).run()
repositorySearch = lambda title, repository, deleteWhenViewed = False, extraItemOptions = None: searchItem(title, RepositoryMenu(title, repository, deleteWhenViewed, extraItemOptions))
repositoryInsert = lambda title, repository, defaults = None, runAfter = lambda _: None: createNewItem(title, repository, defaults, runAfter)
resetUserPassword = lambda id, model: [MenuOption("Reset password (generate temporary password)", lambda: resetPassword(id, model))]
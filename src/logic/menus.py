# The main menu; the entry point into the application

from logic.interface import Menu, MenuOption, RepositoryMenu
import authentication.user
import storage.repositories

# Initialize the repositories
#membersRepository = storage.repositories.Members()
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
    # MenuOption("Change your password", logic.users.changePassword, "password"),
    # MenuOption("List users and roles", lambda: repositoryMenu("User overview", usersRepository).run(), usersRepository.canRead(None)),
    # MenuOption("Create a new user", lambda: repositoryInsert("Create a new user", usersRepository).run(), usersRepository.canInsert()),
    # MenuOption("Search members", logic.members.addMember),
    # MenuOption("Add new member", lambda: None),
    # MenuOption("Backup or Restore", lambda: None),
    MenuOption("View system logs", lambda: repositoryMenu("View system logs", logsRepository).run(), logsRepository.canRead(None)),
    MenuOption("View new suspicious logs", lambda: repositoryMenu("View new suspicious logs", suspiciousLogsRepository, True).run(), suspiciousLogsRepository.canRead(None)),
    MenuOption("Log out (quit program)", lambda: True),
], mainMenuAction)

# Function to generate a repository menu interface
repositoryMenu = lambda title, repository, deleteWhenViewed = False: RepositoryMenu(title, repository, deleteWhenViewed)
repositoryInsert = lambda title, repository: None
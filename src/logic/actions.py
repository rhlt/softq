# Logic for actions that fall outside the menus and repository table view

import datetime
import os
import validation.fields
import validation.forms
import authentication.user
import authentication.logging
import storage.backup
import storage.encryption
import storage.repositories


def changePassword(currentPassword = None):
    """Allow current user to change their password"""

    print() # newline
    if not authentication.user.requireAccess("nothardcoded", "Change password", "Illegal attempt to change own password", True):
        return
    authentication.user.changePassword()


def createNewItem(title, repository, fixedValues = None, runAfter = lambda _: None):
    """Create a new item in a repository, with default values available"""

    print() # newline
    print(title)
    print("*" * len(title))

    print("Please complete all fields or press Ctrl+C to cancel")

    if fixedValues is None:
        fixedValues = {}
    
    model = repository.form.run(fixedValues, fixedValues.keys())
    if model is None:
        return # Canceled
    
    # Allow some last changes to be made
    runAfter(model)
    
    if repository.idField is not None and repository.idField in model and repository._one(model[repository.idField]) is not None:
        # Item with this ID already exists!
        print(f"{repository.form.name} with {repository.form.fields[repository.idField].name} '{model[repository.idField]}' already exists!")
    elif repository.insert(model):
        # Insertion was successful
        print(f"{repository.form.name} added successfully")
    else:
        # Insertion was not successful (?)
        print(f"Failed to add {repository.form.name} (please check the logs)")
    validation.fields.EmptyValue(f"Press enter to go back").run()


def searchItem(title, repositoryMenu):
    """Search an item in a repository menu"""
    
    print() # newline
    print(title)
    print("*" * len(title))

    search = validation.fields.Text(f"Search term").run()
    if search is None:
        return
    
    repositoryMenu.search = search
    return repositoryMenu.run()


def hashGeneratedPassword(model):
    """Hash a generated model password"""
    password = model["password"]
    print("Generated a temporary password: " + password)
    authentication.logging.log("Generated temporary password", f"User: {model['username']}")
    model["password"] = storage.encryption.hashDataWithSalt(password)


def resetPassword(id, model):
    """Reset a user's password (generates a temporary password)"""
    result = validation.fields.Text(f"Are you sure you want to reset the password for {model['username']}? (Y/N)", [validation.rules.valueInList(["Y", "N"])]).run()
    if result is None or result.upper() != "Y":
        return
    model["password"] = storage.encryption.tempPassword()
    hashGeneratedPassword(model) # Hashes newly generated password and shows it on screen
    repository = storage.repositories.Users()
    if repository.update(id, model):
        # Update was successful
        print(f"The password has been reset")
    else:
        # Update was not successful (?)
        print(f"Failed to reset the password (please check the logs)")
    validation.fields.EmptyValue(f"Press enter to continue").run()


def allowBackup():
    """Check if the current user is allowed to create or restore backups"""
    return authentication.user.requireAccess("admin", "Backup", "Attempt to access the backup functionalities")


def createBackup():
    """Create a backup of the database"""

    title = "Create database backup"
    print() # newline
    print(title)
    print("*" * len(title))

    if not allowBackup():
        return
    
    # Access local data
    users = storage.repositories.Users()
    members = storage.repositories.Members()
    logsPath = "./output/logs"

    # Access backup data
    backupPath = "./backups"
    if not os.path.isdir(backupPath):
        os.mkdir(backupPath)
    backupDb = backupPath + "/.temp-backup"
    backupLogs = backupPath + "/.temp-logs"

    usersBackup = storage.repositories.Users(backupDb)
    membersBackup = storage.repositories.Members(backupDb)

    print()
    print("Backing up database...")
        
    storage.backup.backupRepository(users, usersBackup)
    storage.backup.backupRepository(members, membersBackup)

    if os.path.exists(logsPath):
        # Copy over logs
        with open(logsPath, "r") as file:
            content = file.read()
        with open(backupLogs, "w") as file:
            file.write(content)
    elif os.path.exists(backupLogs):
        # Don't keep old temporary backup files
        os.unlink(backupLogs) 

    zipName = "backup" + str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')) + ".zip"
    outputPath = backupPath + "/" + zipName
    print()
    print("Zipping database and logs...")
    zippedFiles = { backupDb: "database", backupLogs: "logs" }
    storage.backup.zip(zippedFiles, outputPath)
    for file in zippedFiles:
        # Remove temporary files
        os.unlink(file)

    if os.path.exists(outputPath):
        print(f"The database and logs were backed up to '{zipName}'")
    else:
        print("Something went wrong during the backup. Check the logs for more information.")
    validation.fields.EmptyValue(f"Press enter to continue").run()


def selectBackup(title):
    """Select a backup file for inspection or restoration"""

    print() # newline
    print(title)
    print("*" * len(title))

    if not allowBackup():
        return

    # Access backup data
    backupFiles = storage.backup.getBackupFiles()

    if backupFiles is None or len(backupFiles) == 0:
        print("There are no backups to restore")
        validation.fields.EmptyValue(f"Press enter to continue").run()
        return
    
    # Ask what file to open
    print("Please enter the filename of the backup to restore. This must be an existing ZIP file in the 'backups' folder.")
    return validation.fields.FromList("Backup file", backupFiles).run()
    

def restoreBackup():
    """Restore a backup file"""

    file = selectBackup("Restore database backup")
    if file is None:
        return # Canceled
    
    # Access backup data
    backupPath = "./backups"
    if not storage.backup.unzip(backupPath + "/" + file, "database", backupPath):
        print("The selected file does not contain a database to restore")
        validation.fields.EmptyValue(f"Press enter to continue").run()
        return

    overwrite = validation.fields.Text(f"Do you want to overwrite items that already exist in the live database? (Y/N, or Ctrl+C to cancel)", [validation.rules.valueInList(["Y", "N"])]).run()
    if overwrite is None:
        return # Canceled
    
    overwrite = overwrite.upper() == "Y"

    backupDb = backupPath + "/database"
    usersBackup = storage.repositories.Users(backupDb)
    membersBackup = storage.repositories.Members(backupDb)

    print()
    print("Restoring backup '" + file + "'...")
    
    users = storage.repositories.Users()
    members = storage.repositories.Members()
    storage.backup.backupRepository(usersBackup, users, overwrite)
    storage.backup.backupRepository(membersBackup, members, overwrite)

    if os.path.exists(backupDb):
        os.unlink(backupDb)
        print("Finished restoring backup")
    else:
        print("Something went wrong during the backup restoration. Check the logs for more information.")
    validation.fields.EmptyValue(f"Press enter to continue").run()
    return


def extractBackupLogs(showMenu):
    
    file = selectBackup("View backed up logs")
    if file is None:
        return # Canceled
    
    # Access backup data
    backupPath = "./backups"
    backupLogs = backupPath + "/logs"
    if not storage.backup.unzip(backupPath + "/" + file, "logs", backupPath):
        print("The selected file does not contain logs to restore")
        validation.fields.EmptyValue(f"Press enter to continue").run()
        return
    
    # Show Logs repository menu
    result = showMenu("View logs in " + file, backupLogs)

    if os.path.exists(backupLogs):
        # Clean up temporary file
        os.unlink(backupLogs)

    return result


# Backup functionality

import os
import re
import zipfile

def zip(files, outputZip):
    """Zip a list of files"""
    with zipfile.ZipFile(outputZip, 'w') as file:
        for f in files:
            if os.path.exists(f):
                file.write(f, files[f])


def unzip(zip, name, outputPath):
    """Unzip a file from a zip file"""
    if not os.path.isdir(outputPath):
        os.mkdir(outputPath)
    with zipfile.ZipFile(zip, 'r') as file:
        if name not in file.namelist():
            return False
        file.extract(name, outputPath)
        return True


def backupRepository(source, target, overwrite = True):
    """Backup a repository from a source to a target"""

    # Copy everything from one repository to another
    offset = 0
    limit = 20
    itemsInserted = 0
    itemsUpdated = 0
    itemsSkipped = 0
    itemsFailed = 0
    while True:
        results = source.readAll(offset, limit)
        if results is None or len(results) == 0:
            break # Finished
        for id in results:
            # Decide what to do with the items we found
            if target.exists(id):
                # This id from source already exists in the target
                if not overwrite:
                    # Exists, not allowed to overwrite
                    itemsSkipped += 1
                elif target.update(id, results[id]):
                    # Successfully updated
                    itemsUpdated += 1
                else:
                    # Something went wrong (logs are maintained by repository)
                    itemsFailed += 1
            else:
                # Does not exist, try to insert it
                if target.insert(results[id]):
                    # Successfully inserted
                    itemsInserted += 1
                else:
                    # Something went wrong (logs are maintained by repository)
                    itemsFailed += 1
        offset += limit

    print(f"  {itemsInserted} {source.name} saved")
    if itemsUpdated > 0:
        print(f"  {itemsUpdated} existing {source.name} updated")
    if itemsSkipped > 0:
        print(f"  {itemsSkipped} {source.name} were skipped as they already exist")
    if itemsFailed > 0:
        print(f"  {itemsFailed} {source.name} could not be saved (check the logs for more information)")


def getBackupFiles():
    """Get available backup files"""

    backupPath = "./backups"
    backupFiles = []
    if os.path.isdir(backupPath):
        for file in os.scandir(backupPath):
            if re.search(r'\.zip$', file.path) and os.path.isfile(file.path):
                backupFiles.append(file.name)

    return backupFiles
"""
Assignment for Analysis 8, Software Quality (INFSWQ21-A)
Name: Ruben Holthuijsen
Student number: 1064459

Requires 'cryptography' package (run "pip install cryptography")
"""

import authentication.logging
import storage.encryption
import logic.menus


# TESTING
import storage.repositories
storage.encryption.initializeKey()
logic.menus.repository("TEST LOGS REPOSITORY", storage.repositories.Logs()).run()
# END TESTING

if __name__ == '__main__0':
    
    try:
        # Generate encryption key
        if storage.encryption.initializeKey():
            authentication.logging.log("Generated new encryption key") # Should be done only once
        
        # Run the main logic
        logic.menus.main.run()

    except Exception as e:
        # Log any exceptions that may occur
        authentication.logging.log("Exception: " + str(e), True)
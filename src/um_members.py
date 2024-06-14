"""
Assignment for Analysis 8, Software Quality (INFSWQ21-A)
Name: Ruben Holthuijsen
Student number: 1064459

Requires 'cryptography' package (run "pip install cryptography")
"""

import auth.logging
import storage.encryption
import logic.menus


storage.encryption.initializeKey()
import storage.files
test = storage.files.Logs()
test.insert({ "timestamp": "a", "message": "b", "username": "", "suspicious": "" })


if __name__ == '__main__':
    
    try:
        # Generate encryption key
        if storage.encryption.initializeKey():
            auth.logging.log("Generated new encryption key") # Should be done only once
        
        # Run the main logic
        logic.menus.main.run()

    except Exception as e:
        # Log any exceptions that may occur
        auth.logging.log("Exception: " + str(e), True)
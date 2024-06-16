"""
Assignment for Analysis 8, Software Quality (INFSWQ21-A)
Name: Ruben Holthuijsen
Student number: 1064459

Requires 'cryptography' package (run "pip install cryptography")
"""

import authentication.logging
import storage.encryption
import logic.menus

if __name__ == '__main__':
    
    # try:
        # Generate encryption key
        if storage.encryption.initializeKeys():
            authentication.logging.log("Generate encryption keys", "This is done automatically if the keys do not exist yet") # Should be done only once
        
        # Run the main logic
        logic.menus.main.run()

    # except Exception as e:
        # Log any exceptions that may occur
        # authentication.logging.log("Exception occured", str(e), True)
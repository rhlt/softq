# Helper functions for data encryption

import hashlib
import os
import random
from cryptography.fernet import Fernet

encryptor = None

def hashData(data):
    """Hash string data"""

    if isinstance(data, str):
        data = data.encode("utf-8")
    if not isinstance(data, bytes):
        return None
    return hashlib.sha256(data).hexdigest()


def hashDataWithSalt(data, saltlen = 8):
    """Hash string data with a random salt"""

    if isinstance(data, str):
        data = data.encode("utf-8")
    if not isinstance(data, bytes):
        return None
    salt = random.randbytes(saltlen)

    # Return both salt and hash
    return salt.hex() + 'x' + hashData(salt + data)


def checkDataHash(data, hash):
    """Check if a hash is valid for this data"""
    
    if not isinstance(data, str) or not isinstance(hash, str):
        return None
    parts = hash.split("x")
    if len(parts) > 1:
        salt = parts[0] # First part up to "x" is the salt
        hash = "x".join(parts[1:]) # The rest is the hash
    else:
        salt = "" # There is no salt
    
    # Compare the hash with the expected hash
    return hashData(bytes.fromhex(salt) + data.encode("utf-8")) == hash
    

def initializeKeys():
    """Ensure an encryption key exists"""
    global encryptor

    if encryptor is not None:
        return False # Already initialized
    
    try:
        # Try loading the key from a file
        if not os.path.isdir('./output'):
            os.mkdir("./output")
        with open("./output/.key", "rb") as file:
            key = file.read()
        encryptor = Fernet(key)
        return False # Key already generated
    except:
        # If file does not exist or it is invalid, generate a new one
        if not os.path.isdir('./output') or not os.access('./', os.R_OK) or not os.access('./', os.W_OK):
            print("Please make sure the working directory and all required files and subfolders are accessible to the application")
            exit()
        key = Fernet.generate_key()
        with open("./output/.key", "wb") as file:
            file.write(key)
        encryptor = Fernet(key)
        return True # Key was generated
            


def encrypt(data):
    """Symmetrically encrypt data"""
    global encryptor
    data = str(data)
    if encryptor is None:
        initializeKeys()
    return encryptor.encrypt(data.encode("utf-8")).decode("utf-8")


def decrypt(data):
    """Symmetrically decrypt data"""
    global encryptor
    if encryptor is None:
        initializeKeys()
    return encryptor.decrypt(data.encode("utf-8")).decode("utf-8")    


def tempPassword():
    """Generate a temporary password: a password that does not validate (no special chars) and therefore forces a password change at next login"""
    characters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789"
    return "".join([random.choice(characters) for _ in range(12)])

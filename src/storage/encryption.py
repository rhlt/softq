# Helper functions for data encryption

import random
import hashlib
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
    

def initializeKey():
    """Ensure an encryption key exists"""
    global encryptor

    if encryptor is not None:
        return False # Already initialized
    
    try:
        # Try loading the key from a file
        with open("./output/.key", "rb") as file:
            key = file.read()
        encryptor = Fernet(key)
        return False # Key already generated
    except:
        # If file does not exist or it is invalid, generate a new one
        key = Fernet.generate_key()
        with open("./output/.key", "wb") as file:
            file.write(key)
        encryptor = Fernet(key)
        return True # Key was generated


def encrypt(data):
    """Symmetrically encrypt data"""
    global encryptor
    return data ### TESTING
    data = str(data)
    return encryptor.encrypt(validation.encode("utf-8")).decode("utf-8")


def decrypt(data):
    """Symmetrically decrypt data"""
    global encryptor
    return data ### TESTING
    try:
        return encryptor.decrypt(validation.encode("utf-8")).decode("utf-8")
    except:
        return None # Corrupted
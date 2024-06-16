# Helper functions for data encryption

import base64
import hashlib
import os
import random

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

privateKey = None
publicKey = None

def hashData(data):
    """Hash string data"""

    if isinstance(data, str):
        data = data.encode()
    if not isinstance(data, bytes):
        return None
    return hashlib.sha256(data).hexdigest()


def hashDataWithSalt(data, saltlen = 8):
    """Hash string data with a random salt"""

    if isinstance(data, str):
        data = data.encode()
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
    return hashData(bytes.fromhex(salt) + data.encode()) == hash
    

def initializeKeys():
    """Ensure an encryption key exists"""
    global privateKey, publicKey

    if privateKey is not None and publicKey is not None:
        return False # Already initialized
    
    try:
        # Try loading the key from a file
        if not os.path.isdir('./output'):
            os.mkdir("./output")
            with open("./output/.private-key", "rb") as file:
                privateKey = serialization.load_pem_private_key(file.read(), password=None, backend=default_backend())
            # Load the public key from a file
            with open("./output/.public-key", "rb") as file:
                publicKey = serialization.load_pem_public_key(file.read(), backend=default_backend())
    except Exception as e:
        print("## ERROR", str(e))
        exit()
        pass
    finally:
        if publicKey is not None and publicKey is not None:
            return False # Initialization worked
        # If files do not exist or are invalid, generate a new key pair
        if not os.path.isdir('./output') or not os.access('./', os.R_OK) or not os.access('./', os.W_OK):
            print("Please make sure the working directory and all required files and subfolders are accessible to the application")
            exit()
        privateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )
        publicKey = privateKey.public_key()
        with open("./output/.private-key", "wb") as file:
            file.write(privateKey.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open("./output/.public-key", "wb") as file:
            file.write(publicKey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        return True # Keys were generated


def encrypt(data):
    """Asymmetrically encrypt data"""
    global publicKey
    data = str(data)
    if publicKey is None:
        initializeKeys()

    return base64.b64encode(publicKey.encrypt(data.encode(), padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))).decode()


def decrypt(data):
    """Asymmetrically decrypt data"""
    global privateKey
    if privateKey is None:
        initializeKeys()
    return privateKey.decrypt(base64.b64decode(data.encode()), padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )).decode()


def tempPassword():
    """Generate a temporary password: a password that does not validate (no special chars) and therefore forces a password change at next login"""
    characters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789"
    return "".join([random.choice(characters) for _ in range(12)])

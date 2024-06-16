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
from cryptography.fernet import Fernet

privateKey = None
publicKey = None
encryptor = None

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
    global privateKey, publicKey, encryptor

    if privateKey is not None and publicKey is not None and encryptor is not None:
        return False # Already initialized
    
    try:
        # Try loading the keys from files
        if not os.path.isdir('./output'):
            os.mkdir("./output")
        # Load the private key
        with open("./output/.private-key", "rb") as file:
            privateKey = serialization.load_pem_private_key(file.read(), password=None, backend=default_backend())
        # Load the public key
        with open("./output/.public-key", "rb") as file:
            publicKey = serialization.load_pem_public_key(file.read(), backend=default_backend())
        if not os.path.isdir('./output'):
            os.mkdir("./output")
        # Load and decrypt the Fernet key for symmetric entryption
        with open("./output/.key", "rb") as file:
            key = decryptAsymmetric(file.read())
        encryptor = Fernet(key)
        return False # Key already generated
    except:
        pass
    finally:
        if publicKey is None or publicKey is None:
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
        if encryptor is None:
            key = Fernet.generate_key()
            with open("./output/.key", "wb") as file:
                file.write(encryptAsymmetric(key))
            encryptor = Fernet(key)
        return True # Keys were generated


def encryptAsymmetric(data):
    """Asymmetrically encrypt data"""
    global publicKey
    if publicKey is None:
        initializeKeys()
    return publicKey.encrypt(data, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))


def decryptAsymmetric(data):
    """Asymmetrically decrypt data"""
    global privateKey
    if privateKey is None:
        initializeKeys()
    return privateKey.decrypt(data, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))


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

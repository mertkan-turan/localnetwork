import pickle
from cryptography.fernet import Fernet

key = Fernet.generate_key()

with open("./key", "wb") as key_file:
    pickle.dump(key, key_file)
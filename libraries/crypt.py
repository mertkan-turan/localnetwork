import socket
import pickle
from cryptography.fernet import Fernet

# key = Fernet.generate_key()

class Crypto():
    def __init__(self):
        self.key = self.get_key()
        self.cipher_suite = self.get_cipher_suite()
  
    def get_key(self):
        with open("./key", "rb") as key_file:
            key = pickle.load(key_file)
        return key
    

    def get_cipher_suite(self):
        cipher_suite = Fernet(self.key)
        return cipher_suite
    
    def encrypt_message(self, message):
        encrypted_message = self.cipher_suite.encrypt(message.encode())
        return encrypted_message
    
    def decrypt_message(self, encrypted_message):
        decrypted_message = self.cipher_suite.decrypt(encrypted_message).decode()
        return decrypted_message






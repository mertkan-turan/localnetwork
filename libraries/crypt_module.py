import pickle
from cryptography.fernet import Fernet
import threading

# key = Fernet.generate_key()

class Crypto():
    def __init__(self):
        # self.key = self.create_key()
        self.key = ""
        
        # self.cipher_suite = self.create_cipher_suite()
        self.cipher_suite = None
  
    def create_key(self, write_to_file=False):
        self.key = Fernet.generate_key()
        
        if write_to_file:
            with open("./key", "wb") as key_file:
                pickle.dump(self.key,key_file)
        
        return self.key
    
    def set_key(self, key):
        self.key = key
        self.cipher_suite = self.create_cipher_suite()
    
    def get_key_file(self):
        with open("./key", "rb") as key_file:
            key = pickle.load(key_file)
        return key

    def create_cipher_suite(self):
        self.cipher_suite = Fernet(self.key)
        return self.cipher_suite
    
    def encrypt_message(self, message):
        if self.cipher_suite:
            encrypted_message = self.cipher_suite.encrypt(message.encode())
            return encrypted_message
        else:
            raise Exception("No cipher suite created. Please create a cipher suite first.")
    
    def decrypt_message(self, encrypted_message):
        if self.cipher_suite:
            decrypted_message = self.cipher_suite.decrypt(encrypted_message).decode()
            return decrypted_message
        else:
            raise Exception("No cipher suite created. Please create a cipher suite first.")


if __name__ == "__main__" :
      print(threading.active_count())
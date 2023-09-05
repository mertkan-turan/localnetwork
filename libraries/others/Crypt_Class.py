import pickle
from cryptography.fernet import Fernet
import threading

# key = Fernet.generate_key()

class Crypto():
    def __init__(self):
        # self.key = self.create_key()
        self.key:str|bytes = ""
        
        # self.cipher_suite = self.create_cipher_suite()
        self.cipher_suite:Fernet
  
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
    
    def encrypt_message(self, message:str):
        if self.cipher_suite:
            # print(f"[DEBUG] Message Encryption -> '{message}':{len(message.encode())}")
            encrypted_message = self.cipher_suite.encrypt(message.encode())
            # print(f"[DEBUG] Message Encrypted -> {len(encrypted_message)}")
            return encrypted_message
        else:
            raise Exception("No cipher suite created. Please create a cipher suite first.")
    
    def decrypt_message(self, encrypted_message: bytes | str):
        if self.cipher_suite:
            decrypted_message = self.cipher_suite.decrypt(encrypted_message).decode()
            return decrypted_message
        else:
            raise Exception("No cipher suite created. Please create a cipher suite first.")


if __name__ == "__main__" :
    crypto = Crypto()
    user_response = input("Create new key? (y/n): ")
    
    if user_response == "y":
        crypto.create_key(write_to_file=True)
    else:
        user_response = input("Load from key file (y/n): ")
        if user_response == "y":
            crypto.set_key(crypto.get_key_file())
        else:
            user_response = input("Key: ")
            crypto.set_key(user_response.encode())
            
    print(f"Key: {crypto.key}")

    crypto.create_cipher_suite()

    is_decrypt = input("Decrypt? (y/n): ")
    encoding = input("Encoding [default is 'utf-8']: ")
    if encoding == "":
        encoding = "utf-8"

    print("Exit with ':qw'")
    while True:
        user_response = input("Message: ")
        
        # Actions
        if user_response == ":qw":
            print(f"Exiting...")
            break
        
        # Encryption / Decryption

        print(
            f"user_response [str_len: {len(user_response)} - byte_len: {len(user_response.encode(encoding))}]: {user_response}"
        )
        if is_decrypt == "y":
            decrypted = crypto.decrypt_message(user_response)
            print(f"Decrypted [str_len: {len(decrypted)} - byte_len: {len(decrypted.encode(encoding))}]: {decrypted}")

        else:
            encrypted = crypto.encrypt_message(user_response)
            print(
                f"Encrypted [byte_len: {len(encrypted)} - str_len: {len(encrypted.decode(encoding))}]: {encrypted}"
            )

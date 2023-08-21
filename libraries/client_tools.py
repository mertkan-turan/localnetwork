import socket
import errno
import logging
import time
from libraries.crypt_module import Crypto
import pickle
from cryptography.fernet import Fernet

class Client:

    def __init__(self,username):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.client.setblocking(False)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logging.basicConfig(filename='client_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.logger = logging.getLogger()
        
        self.username = username

        # TODO: Fix
        self.switch = None
        self.crypto_module = Crypto()
        
    def setup_logger(self):
        logger = logging.getLogger("ClientLogger")
        logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler('client_log.txt')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()  
        console_handler.setLevel(logging.DEBUG)  
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)  
        
        return logger
    
    def connect(self, ip_address, port):
        try:
            self.logger.info("Connecting to server: %s:%s", ip_address, port)
            self.client.connect((ip_address, int(port)))
            #if self.switch is None: 
            #    self.switch = self.client.recv(1024)
            print("Key transmission started...")
            
            # TODO: Fix
            start_time = time.time()
            key = ""
            key_received = False
            key_pattern = "KEY_RECEIVED"
            while not key_received:
                passed_time = start_time - time.time()
                if passed_time > 10:
                    raise Exception ("Key pattern time out...")
                
                print("Key waiting from server...")
                key_pattern_message = self.client.recv(1024)
                #print("Key pattern message received:", key_pattern_message.decode())
                
                if key_pattern_message.decode() == "!KEY:":
                    print("Key pattern received...")
                    while True:
                        key = self.client.recv(44)
                        if key != "":
                            print("Key received:", key.decode())
                            key_received = True
                            self.client.sendall(key_pattern.encode())
                            print("Key received information sent to server:", ip_address)
                            break
            
            self.crypto_module.set_key(key)
            
            print("Successfully connected to server:", ip_address, ":", port)
            print("If you want to exit program,please write exit!! ")
            while True:
                message =  input("Enter a message: ")  
                
                encrypted_message = self.crypto_module.encrypt_message(message)
                self.client.sendall(encrypted_message)
                # self.client.sendall(message.encode())
                
                print(f"Sent by {self.username}:{message}")
                
                # TODO: Fix
                if(message == "EXIT" or message == "Exit" or message == "exit"):
                    print("Are you sure you want to close the program? (Yes No)")
                    answer = input("Answer:")
                    if(answer == "Yes" or answer == "yes" or "YES"):    
                        print("Program is closing..")
                        break
                    else:
                        continue
                    break
                else:
                    continue


        except socket.timeout:
            self.logger.warning("Connection is waiting...")
            self.client.close()
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                self.logger.error("Connection Refused.")
            else:
                self.logger.error("Socket error: %s", e)
                self.logger.error("Error message: %s", e.strerror)
            return False
        except Exception as e:
            self.logger.error("Exception: %s", e)
            return False

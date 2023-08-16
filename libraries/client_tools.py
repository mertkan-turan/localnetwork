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
        logging.basicConfig(filename='client_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.logger = logging.getLogger()
        
        self.username = username
        self.keycik = None
        self.crypto_module = Crypto()
        
 
    
    def connect(self, ip_address, port):
        try:
            print("Connecting to server:", ip_address, ":", port)
            self.client.connect((ip_address, int(port)))
            #if self.keycik is None: 
            #    self.keycik = self.client.recv(1024)
            print("Key transmission started...")
            
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
                            print("Key received information sent to server:")
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
            print("Connection is waiting...")
            self.client.close()
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                print("Connection Refused.")
            else:
                print("Socket error.", e)
                print("Error message:", e.strerror)
            return False
        except Exception as e:
            print("Exception:", e)
            return False

import socket
import errno
import logging
from libraries.crypt import Crypto


class Client:

    def __init__(self,username):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logging.basicConfig(filename='client_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()
        self.username = username
        self.crypto_module = Crypto()
        
    def connect(self, ip_address, port):
        try:
            self.client.connect((ip_address, int(port)))
            print("Successfully connected to server")
            print("If you want to exit program,please write exit!! ")
            while True:
                message =  input("Enter a message: ")  
                
                encrypted_message = self.crypto_module.encrypt_message(message)
                self.client.sendall(encrypted_message)             
                self.logger.info("Sent by %s: %s",self.username, message)
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

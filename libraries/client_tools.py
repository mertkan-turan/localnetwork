import socket
import errno
import tkinter as tk
import logging
from tkinter import scrolledtext
from tkinter import messagebox

class Client:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Initialize the logging configuration
        logging.basicConfig(filename='client_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()
    def connect(self, ip_address, port):
        try:
            self.client.connect((ip_address, int(port)))
            print("Successfully connected to server")
            print("If you want to exit program,please write exit!! ")
            self.logger.info("Successfully connected to server")
            self.logger.info("If you want to exit program, please write exit!! ")
            while True:

                message = input("Enter a message: ")
                self.client.sendall(message.encode())
                self.logger.info("Sending: %s", message)  # Log the message before sending
                if(message == "EXIT" or message == "Exit" or message == "exit"):
                    print("Are you sure you want to close the program? (Yes No)")
                    answer = input("Answer:")
                    if(answer == "Yes" or answer == "yes" or "YES"):    
                        print("Program is closing..")
                        break
                    else:
                        continue
                    
                else:
                    continue


        except socket.timeout:
            messagebox.showerror("Connection is waiting...")
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

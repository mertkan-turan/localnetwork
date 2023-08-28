import socket
import logging
import sys
import threading
import time
from Libraries.Classes.Crypt_Class import Crypto
from abc import ABC, abstractmethod
from Libraries.Tools.network_tools import get_ip

class SocketInterface(ABC):
    def __init__(self,port,username,is_encrypted:bool,is_server:bool,logging_name:str = ""):
        self.port = port
        self.username = username
        self.is_encrypted = is_encrypted
        
        self.ip = get_ip()
        self.logger = logging.getLogger(logging_name)
        
        self.create_socket(is_server)
        self.init_threads()
        self.configure_logger()
    
    
    @abstractmethod
    def init_threads(self):
        pass
    
    def create_socket(self,is_server:bool,listen_number = 0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        if is_server == True:
            self.socket.bind((socket.gethostname(), self.port))
            if listen_number != 0:
                self.socket.listen(listen_number)

    
    def configure_logger(self):
        self.logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler('server_log.txt')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        
        self.logger.addHandler(stream_handler)

    
    def send_message(self, connection, message, send_pattern="", receive_pattern="", timeout=3):
        if send_pattern != "":
            start_time = time.time()
            end_time = time.time()

            while end_time - start_time < timeout:
                # Timeout Control
                end_time = time.time()

                # Send Action
                try:
                    connection.send(send_pattern.encode())
                    connection.send(message.encode())
                except Exception as error:
                    self.logger.error(f"Error message: {error.args, error.__str__()}")

                # Is Received Response
                receive_message = connection.recv(1024)

                if receive_message.decode() == receive_pattern:
                    # message be sended successfully
                    return 0
                
            # If timeout occurred, message NOT be sended
            return -1
        else:
            try:
                connection.send(message.encode())
                return 0
            except Exception as error:
                self.logger.error(f"Error message: {error.args, error.__str__()}")
                return -1

    @staticmethod
    def receive_messages():
        # Implement the receive_messages function logic here
        pass
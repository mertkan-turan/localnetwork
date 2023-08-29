import socket
import logging
import sys
import threading
import time
from Libraries.Classes.Crypt_Class import Crypto
from abc import ABC, abstractmethod
from Libraries.Tools.network_tools import get_ip

class SocketInterface(ABC):
    def __init__(self, port:int, username:str, is_encrypted: bool, is_server: bool, logging_name: str = ""):
        self.port = port
        self.username = username
        self.is_encrypted = is_encrypted
        self.crypto_module = None

        self.__timeout_pattern = "!*TIMEOUT*!"


        self.ip = get_ip()
        self.logger = logging.getLogger(logging_name)
        
        self.create_socket(is_server)
        self.init_threads()
        self.configure_logger()

        # Crypto Module Initialization
        if self.is_encrypted:
            self.crypto_module = Crypto()
            self.switch = self.crypto_module.create_key()
            self.crypto_module.create_cipher_suite()
    
    
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

    
    def send_message(self, local_socket, message, send_pattern="", receive_pattern="", timeout=3):
        if send_pattern != "":
            start_time = time.time()
            end_time = time.time()

            while end_time - start_time < timeout:
                # Timeout Control
                end_time = time.time()

                # Send Action
                try:
                    local_socket.sendall(send_pattern.encode())
                    local_socket.sendall(message.encode())
                except Exception as error:
                    self.logger.error(f"Error message: {error.args, error.__str__()}")

                # Is Received Response
                response = False
                
                response, receive_message = self.receive_messages(
                    local_socket=local_socket, 
                    timeout=timeout
                )

                if receive_message == receive_pattern:
                    # message be sended successfully
                    return 0
                
            # If timeout occurred, message NOT be sended
            return -1
        else:
            try:
                local_socket.sendall(message.encode())
                return 0
            except Exception as error:
                self.logger.error(f"Error message: {error.args, error.__str__()}")
                return -1


    def decrypt_message(self, message:str):
        if self.is_encrypted and self.crypto_module is not None:
            message = self.crypto_module.decrypt_message(message)
        return message


    def receive_messages(self, local_socket:socket.socket, pattern_received="", pattern_received_response="", timeout:int=3) -> tuple[bool, str]:
        message = ""

        # If pattern received is not empty, then we will wait for the pattern
        if pattern_received != "":
            start_time = time.time()
            end_time = time.time()
            
            # PATTERN HOOK
            while message != pattern_received:
                end_time = time.time()
                
                if end_time - start_time > timeout:
                    return False, self.__timeout_pattern

                message = self.decrypt_message(
                    local_socket.recv(1024).decode()
                )
                
            # MESSAGE HOOK
            message = ""
            while message == "":
                end_time = time.time()

                if end_time - start_time > timeout:
                    return False, self.__timeout_pattern
                
                message = self.decrypt_message(
                    local_socket.recv(1024).decode()
                )
            self.send_message(local_socket=self.socket, message=pattern_received_response)
            
        else:
            # Receive message without pattern
            message = self.decrypt_message(
                local_socket.recv(1024).decode()
            )

        return True, message


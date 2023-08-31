import socket
import logging
import sys
import threading
import time
from typing import ByteString
from Libraries.Classes.Crypt_Class import Crypto
from abc import ABC, abstractmethod
from Libraries.Tools.network_tools import get_ip

class SocketInterface(ABC):
    def __init__(self, port:int, username:str, is_encrypted: bool, is_server: bool, logging_name: str = ""):
        self.port = port
        self.username = username
        self.is_encrypted = is_encrypted
        self.crypto_module = None
        self.is_socket_closing = False
        self.is_server = is_server    # Optional, can be deleted
        
        self.message_max_byte_length = 2048

        self.__timeout_pattern = "!*TIMEOUT*!"


        self.ip = get_ip()
        self.logger = logging.getLogger(logging_name)
        
        # self.create_socket(is_server)
        self.configure_logger()

        # Crypto Module Initialization
        if self.is_encrypted:
            self.crypto_module = Crypto()
            self.switch = self.crypto_module.create_key()
            self.crypto_module.create_cipher_suite()
    
    
    @abstractmethod
    def init_threads(self):
        pass
    
    # Global
    #@property
    def is_Socket_Closed(self):
        return self.is_socket_closing


    # Global
    #@is_Socket_Closed.setter
    def set_Socket_Closed(self, shutdown:bool):
        self.is_socket_closing = shutdown
    
    def create_socket(self,is_server:bool,listen_number = -1, timeout_second:int|None = None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(timeout_second)

        if is_server == True:
            self.socket.bind((self.ip, self.port))
            if listen_number != -1:
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

    
    def send_message(self, local_socket, message:str, send_pattern:str="", receive_pattern:str="", timeout=3, encrypt=True):
        message_byte_len = len(message.encode())
        pattern_byte_len = len(send_pattern.encode())
        
        if message_byte_len > self.message_max_byte_length:
            raise Exception(f"Message byte length is too long. Maximum byte length is {self.message_max_byte_length}.")
        elif message_byte_len < self.message_max_byte_length:
            message += "\0" * (self.message_max_byte_length - message_byte_len)
        
        if pattern_byte_len > self.message_max_byte_length:
            raise Exception(f"Pattern byte length is too long. Maximum byte length is {self.message_max_byte_length}.")
        elif pattern_byte_len < self.message_max_byte_length:
            send_pattern += "\0" * (self.message_max_byte_length - pattern_byte_len)
        
        if send_pattern != "":
            start_time = time.time()
            end_time = time.time()
            
            while end_time - start_time < timeout:
                # Timeout Control
                end_time = time.time()

                # Send Action
                try:
                    send_pattern_byte = self.encrypt_message(
                        send_pattern, 
                        encrypt
                    )
                    local_socket.send(send_pattern_byte)
                    message_byte = self.encrypt_message(
                        message, 
                        encrypt
                    )
                    local_socket.send(message_byte)
                except Exception as error:
                    self.logger.error(f"Error message: {error.args, error.__str__()}")


                # Is Received Response
                response, receive_message = self.receive_messages(
                    local_socket=local_socket, 
                    timeout=timeout,
                    decrypt=encrypt
                )
                
                """message = ""
                message = local_socket.recv(self.message_max_byte_length).decode()
                message = message.strip("\0")
                # Receive message without pattern
                receive_message = self.decrypt_message(
                    message=message,
                    decrypt=encrypt
                )"""

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


    def receive_messages(self, local_socket:socket.socket, pattern_received="", pattern_received_response="", timeout:int=3, decrypt:bool=True) -> tuple[bool, str]:
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
                
                try:
                    self.logger.info(f"receiving {pattern_received}")
                    received_message = local_socket.recv(self.message_max_byte_length).decode()
                    self.logger.info(f"received")
                except Exception as error:
                    self.logger.error(f"Error while receiving message.{error.args, error.__str__()}")
                    
                received_message = received_message.strip("\0")
                self.logger.debug(f"pattern_received message: {received_message}")
                message = self.decrypt_message(
                    received_message,
                    decrypt
                )
                
            # MESSAGE HOOK
            message = ""
            while message == "":
                end_time = time.time()

                if end_time - start_time > timeout:
                    return False, self.__timeout_pattern
                
                message = local_socket.recv(self.message_max_byte_length).decode()
                message = message.strip("\0")
                self.logger.debug(f"Received message: {message}")
                message = self.decrypt_message(
                    message,
                    decrypt
                )
                
            self.logger.debug(f"sending pattern_received_response: {pattern_received_response}")
            pattern_received_response_byte = self.encrypt_message(
                pattern_received_response,
                decrypt
            )
            local_socket.sendall(pattern_received_response_byte)
            # TODO: Fix the problem of send_message without pattern
            """self.send_message(
                local_socket=local_socket, 
                message=pattern_received_response,
                encrypt=decrypt
            )"""
            self.logger.debug(f"sent pattern_received_response: {pattern_received_response}")
            
        else:
            message = ""
            message = local_socket.recv(self.message_max_byte_length).decode()
            message = message.strip("\0")
            # Receive message without pattern
            message = self.decrypt_message(
                message,
                decrypt
            )

        return True, message

    def encrypt_message(self, message:str, encrypt:bool) -> ByteString:
        if self.is_encrypted and self.crypto_module is not None and encrypt:
            return self.crypto_module.encrypt_message(message)
        else:
            return message.encode()


    def decrypt_message(self, message:str, decrypt:bool):
        if self.is_encrypted and self.crypto_module is not None and decrypt:
            message = self.crypto_module.decrypt_message(message)
        return message


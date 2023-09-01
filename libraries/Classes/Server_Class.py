import socket
import logging
import sys
import threading
import time
import queue
from typing import Dict, Type, Union

from Libraries.Classes.Crypt_Class import Crypto
from Libraries.Tools.network_tools import get_ip
from Libraries.Classes.Socket_Interface_Class import SocketInterface


class Server(SocketInterface):
    def __init__(self, port:int, username:str, is_encrypted:bool, init_server:bool=True, message_timeout_second: int=10, socket_timeout_second:int|None= None, listen_number:int=1, logging_name:str=""):
        super().__init__(port, username, is_encrypted,is_server = True,logging_name=logging_name)  # Call the superclass's init method

        # Additional attributes specific to Server
        self.init_server = init_server
        self.message_timeout_second = message_timeout_second

        # Logger
        self.logging=self.setup_logger()

        # General Variables
        self.broadcast_message_queue = queue.Queue()
        self.is_server_closing = False

        
        self.__active_connection_template: Dict[
            str, 
            Union[socket.socket, socket._RetAddress, threading.Thread]
        ] = {
            "conn": None,
            "addr": None,
            "thread": None
        }
        # Threads and Connection Variables
        self.global_threads: Dict[
            str, 
            Union[threading.Thread, Dict[
                str, 
                Union[socket.socket, socket._RetAddress, threading.Thread]]]] = {
            "server": threading.Thread(),
            "clients": dict()
        }

        # Will be initialized after
        self.switch = None
        self.crypto_module = None

        # Crypto Module Initialization
        if self.is_encrypted:
            self.crypto_module = Crypto()
            self.switch = self.crypto_module.create_key()
            self.crypto_module.create_cipher_suite()
            
        if init_server:
            self.create_socket(
                is_server = True, 
                listen_number=listen_number,
                timeout_second=socket_timeout_second
            )

        self.init_threads()


    # Global
    def init_threads(self):
        self.global_threads["server"] = threading.Thread(
            target=self.accept_connections,
            daemon=True
        )
        
        self.global_threads["message_broadcaster"] = threading.Thread(
            target=self.message_broadcaster,
            daemon=True
        )

        
    # Global
    def setup_logger(self):
        logger = logging.getLogger("ServerLogger")
        logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler('server_log.txt')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(stream_handler)
        
        return logger  
                          
                             
    def server_serve(self):
        self.logging.info(f"Server IP Address: {self.ip}")
        self.global_threads["server"].start()
        self.global_threads["message_broadcaster"].start()
       
        try:
            while not self.is_Socket_Closed():
                
                # Example: Print a message every 8 seconds
                self.logging.debug("Server is running...")
                time.sleep(15)
                
        except KeyboardInterrupt:
                # self.stop_event.set()
                self.logging.info("Server shutting down due to user interruption.")
                self.stop_server()
    

    # Global
    def stop_server(self):
        self.logging.info("Clients shutting down...")
        
        self.set_Socket_Closed(True)
        
        for client in self.global_threads["clients"].values():
            client["thread"].join()
            client["conn"].close()
        
        self.global_threads["message_broadcaster"].join()    

        self.logging.info("Server shutting down...")
        self.global_threads["server"].join()
        
        if self.socket:
            self.socket.close()
        
        self.logging.info("Server stopped.")

    
    def accept_connections(self):
        
        while not self.is_Socket_Closed():
            time.sleep(0.05)
            
            conn = None
            
            try:
                if self.socket:
                    try:
                        conn, addr = self.socket.accept()
                        # conn.setblocking(False)
                    except Exception as error:
                        self.logging.error(f"Connection Accept Error message: {error.args, error.__str__()}")
                        continue
                    
                    if conn is not None:
                        response, username = self.accept_protocol(conn)
                        
                        if response:
                            temp_conn = self.__active_connection_template.copy()
                            
                            temp_conn["conn"] = conn
                            temp_conn["addr"] = addr
                            temp_conn["thread"] = threading.Thread(
                                target=self.connection_handler,
                                args=(conn, username)
                            )

                            self.global_threads["clients"][username] = temp_conn
                            self.global_threads["clients"][username]["thread"].start()
                            """
                            { # Dict: active_connections (key: username)
                                # value: 
                                { # username
                                    "conn": conn,
                                    "thread": thread
                                },
                                { # username
                                    "conn": conn,
                                    "thread": thread
                                },
                                { # username
                                    "conn": conn,
                                    "thread": thread
                                }
                            }
                            """
                            
                            self.logging.info(f"Connection accepted: {addr}")
                        else:
                            self.logging.info(f"Connection broken (response False): {addr}")
                            
                    
            except socket.timeout:
                self.logging.warn("Connection is waiting.. (Timeout)")
            except Exception as e:
                self.logging.error(f"Connection error: {e.args, e.__str__()}")
    

    def remove_client(self, username):
        self.global_threads["clients"][username]["thread"].join()
        self.global_threads["clients"][username]["conn"].close()

        self.global_threads["clients"].pop(username)

    
    def enqueue_broadcast(self, sender_username, message):
        self.broadcast_message_queue.put((sender_username, message))
    
    def message_broadcaster(self):
        while not self.is_Socket_Closed():
            time.sleep(0.1)
            message = self.broadcast_message_queue.get()
            if message:
                sender_username, message_text = message
                self.broadcast_message(sender_username, message_text)
                
   
    def start_message_broadcaster(self):
        self.global_threads["message_broadcaster"].start()
        
    def broadcast_message(self, sender_username:str, message:str) -> list:
        failed_broadcast_users = list()

        for username, connection_pack in self.global_threads["clients"].items():
            if sender_username != username:
                self.logging.info("Sending message...")

                # is_sended = self.send_message(
                #     local_socket=connection_pack["conn"],
                #     message=f"{sender_username}:{message}",
                # )
                is_sended = self.message_sender(
                    local_socket=connection_pack["conn"],
                    message=f"{sender_username}:{message}",
                    # send_pattern="!MESSAGE:",
                    # receive_pattern="MESSAGE_RECEIVED",
                    timeout=self.message_timeout_second,
                    encrypt=False
                )
                
                if is_sended != 0:
                    failed_broadcast_users.append(username)

        return failed_broadcast_users


    # Global
    def send_key(self, local_socket):
        if self.switch:
            # return self.send_message(
            #     local_socket=local_socket,
            #     message=self.switch.decode(),
            #     send_pattern="!KEY:",
            #     receive_pattern="KEY_RECEIVED",
            #     timeout=5,
            #     encrypt=False
            # )
            return self.message_sender(
                local_socket=local_socket,
                message=self.switch.decode(),
                send_pattern="!KEY:",
                receive_pattern="KEY_RECEIVED",
                timeout=self.message_timeout_second,
                encrypt=False
            )
            
    
    def accept_protocol(self, connection):

        self.logger.info("Accept Protocol: Started")
        if self.is_encrypted:
            self.logger.info("Accept Protocol: Key sending...")
            self.send_key(connection)
            self.logger.info("Accept Protocol: Key sent")
        
        self.logger.info("Accept Protocol: Waiting for username...")
        # response, username = self.receive_messages(
        #     local_socket=self.socket,
        #     pattern_received="!USERNAME:", 
        #     pattern_received_response="USERNAME_RECEIVED",
        #     decrypt=True
        # )
        response, username = self.message_receiver(
            local_socket=self.socket,
            pattern_received="!USERNAME:",
            pattern_received_response="USERNAME_RECEIVED",
            timeout=self.message_timeout_second,
            decrypt=True
        )
        
        if response:
            self.logger.info(f"Accept Protocol: Username received: {username}")
        else:
            self.logger.error(f"Accept Protocol: Username could not be received: {username}")
            
        return response, username
        

    # Global
    def connection_handler(self, connection, username):
        
        while not self.is_Socket_Closed():
            time.sleep(0.03)
            
            # message = self.receive_messages(connection)

            response, message = self.message_receiver(
                local_socket=connection,
                timeout=self.message_timeout_second,
                decrypt=True
            )
            self.logging.info(f"MESSAGE | {username}: [{response}] {message}")
            
            self.enqueue_broadcast(username,message)
            


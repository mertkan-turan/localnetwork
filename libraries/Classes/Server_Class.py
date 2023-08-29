import socket
import logging
import sys
import threading
import time
import queue
from typing import Dict, List

from Libraries.Classes.Crypt_Class import Crypto
from Libraries.Tools.network_tools import get_ip
from Socket_Interface_Class import SocketInterface


class Server(SocketInterface):
    def __init__(self, port, username, is_encrypted, init_server=True, logging_name:str=""):
        super().__init__(port, username, is_encrypted,is_server = True,logging_name=logging_name)  # Call the superclass's init method

        # Additional attributes specific to Server
        self.init_server = init_server    

        # Parameters ..
        self.broadcast_message_queue = queue.Queue()
        # Logger
        self.logging=self.setup_logger()

        # General Variables
        self.hostname=socket.gethostname()   
        self.ip = socket.gethostbyname(self.hostname).replace(",",".") 
        #self.ip = "" #socket.gethostbyname_ex(socket.gethostname())[-1]
        self.ip = get_ip()
        self.broadcast_message_queue = queue.Queue()
        self.is_server_closing = False

        # Threads and Connection Variables
        self.global_threads = {
            "server": None,
            "clients": dict()
        }
        self.__active_connection_template: Dict[
            str, 
            socket.socket | socket._RetAddress | threading.Thread
        ] = {
            "conn": None,
            "addr": None,
            "thread": None
        }

        # Will be initialized after
        self.socket
        self.switch = None
        self.crypto_module = None

        # Crypto Module Initialization
        if self.is_encrypted:
            self.crypto_module = Crypto()
            self.switch = self.crypto_module.create_key()
            self.crypto_module.create_cipher_suite()
            
        if init_server:
            self.create_socket(is_server = True)

        self.init_threads()


    # Global
    #@property
    def is_Server_Closed(self):
        return self.is_server_closing


    # Global
    #@is_Server_Closed.setter
    def set_Server_Closed(self, shutdown:bool):
        self.is_server_closing = shutdown


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
            while not self.is_Server_Closed():
                
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
        
        self.set_Server_Closed(True)
        
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
        
        while not self.is_Server_Closed():
            time.sleep(0.05)
            
            conn = None
            try:
                if self.socket:
                    conn, addr = self.socket.accept()
                    
                    print("connection accepted :" , conn , addr)
                    if conn is not None:
                        # TODO Fix this
                        username = conn.recv(1024).decode('utf-8')  # Receive username from client
                        
                        temp_conn = self.__active_connection_template.copy()
                        
                        temp_conn["conn"] = conn
                        temp_conn["addr"] = addr
                        temp_conn["thread"] = threading.Thread(
                            target=self.connection_handler,
                            args=(conn,username)
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
        while not self.is_Server_Closed():
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

                is_sended = self.send_message(
                    local_socket=connection_pack["conn"],
                    message=f"{sender_username}:{message}",
                )
                if is_sended != 0:
                    failed_broadcast_users.append(username)

        return failed_broadcast_users


    # Global
    def send_key(self, local_socket):
        if self.switch:
            return self.send_message(
                local_socket=local_socket,
                message=self.switch.decode(),
                send_pattern="!KEY:",
                receive_pattern="KEY_RECEIVED",
                timeout=5
            )


    # Global
    def connection_handler(self, connection,username):
        if self.is_encrypted:
            self.send_key(connection)
        
        while not self.is_Server_Closed():
            time.sleep(0.03)
            
            message = self.receive_messages(connection)

            self.logging.info(f"MESSAGE | {username}: {message}")
            
            self.enqueue_broadcast(username,message)
            


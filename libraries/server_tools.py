import socket  
import logging
import sys
from libraries.crypt_module import Crypto
import threading
import time
from queue import Queue
from typing import Dict, List

class Server:
    def __init__(self, port:int, username, is_encrypted:bool=False, init_server:bool=True):
        # Parameters
        self.port = port
        self.username = username
        self.is_encrypted = is_encrypted 

        # Logger
        self.logging=self.setup_logger()

        # General Variables
        self.hostname=socket.gethostname()   
        self.ip = socket.gethostbyname(self.hostname).replace(",",".") 
        #self.ip = "" #socket.gethostbyname_ex(socket.gethostname())[-1]
        self.ip = "localhost"
        self.broadcast_message_queue = list()
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
        self.server = None
        self.switch = None
        self.crypto_module = None

        # Dunno
        self.stop_event = threading.Event()  # Initialize stop_event
        self.lock = threading.Lock()  # Lock for managing shared data

        # Crypto Module Initialization
        if self.is_encrypted:
            self.crypto_module = Crypto()
            self.switch = self.crypto_module.create_key()
            self.crypto_module.create_cipher_suite()
            
        if init_server:
            self.create_server()

        self.init_threads()


    #@property
    def is_Server_Closed(self):
        return self.is_server_closing


    #@is_Server_Closed.setter
    def set_Server_Closed(self, shutdown:bool):
        self.is_server_closing = shutdown


    def init_threads(self):
        self.global_threads["server"] = threading.Thread(
            target=self.accept_connections,
            daemon=True
        )


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
    

    def create_server(self):

        #socket.setdefaulttimeout(50)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, int(self.port)))
        self.server.listen(5)
        # self.server.setblocking(False)

        return self.server
                          
                             
    def server_serve(self):
        self.logging.info(f"Server IP Address: {self.ip}")
        self.global_threads["server"].start()
       
        try:
            while not self.is_Server_Closed():
                
                # Example: Print a message every 8 seconds
                self.logging.debug("Server is running...")
                time.sleep(15)
                
        except KeyboardInterrupt:
                # self.stop_event.set()
                self.logging.info("Server shutting down due to user interruption.")
                self.stop_server()
    

    def stop_server(self):
        self.logging.info("Clients shutting down...")
        
        self.set_Server_Closed(True)
        
        for client in self.global_threads["clients"].values():
            client["thread"].join()
            client["conn"].close()
            
        self.logging.info("Server shutting down...")
        self.global_threads["server"].join()
        
        if self.server:
            self.server.close()
        self.logging.info("Server stopped.")

    
    def accept_connections(self):
        
        while not self.is_Server_Closed():
            time.sleep(0.05)
            
            conn = None
            try:
                if self.server:
                    conn, addr = self.server.accept()
                    
                    print("connection accepted :" , conn , addr)
                    if conn is not None:
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


    def send_message(self, connection:socket.socket, message:str, send_pattern:str="", receive_pattern:str="", timeout:int=3) -> int:
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
                    self.logging.error(f"Error broadcasting message: {error.args, error.__str__()}")

                # Is Received Response
                key_message = connection.recv(1024)

                if key_message.decode() == receive_pattern:
                    # message be sended successfully
                    return 0
                
            # If timeout occurred, message NOT be sended
            return -1
        else:
            try:
                connection.send(message.encode())
                return 0
            except Exception as error:
                self.logging.error(f"Error broadcasting message: {error.args, error.__str__()}")
                return -1


    def broadcast_message(self, sender_username:str, message:str) -> list:
        failed_broadcast_users = list()

        for username, connection_pack in self.global_threads["clients"].items():
            if sender_username != username:
                self.logging.info("Sending message...")

                is_sended = self.send_message(
                    connection=connection_pack["conn"],
                    message=f"{sender_username}:{message}",
                )
                if is_sended != 0:
                    failed_broadcast_users.append(username)

        return failed_broadcast_users


    def task_broadcast_message(self, sender_username:str, message:str) -> list:
        self.broadcast_message_queue = list()

        failed_broadcast_users = list()

        for username, connection_pack in self.global_threads["clients"].items():
            if sender_username != username:
                self.logging.info("Sending message...")

                is_sended = self.send_message(
                    connection=connection_pack["conn"],
                    message=f"{sender_username}:{message}",
                )
                if is_sended != 0:
                    failed_broadcast_users.append(username)

        return failed_broadcast_users

    
    def decrypted_message(self, encrypted_message):
        decrypted_message = ""        
 
        if self.is_encrypted and self.crypto_module:
            decrypted_message = self.crypto_module.decrypt_message(encrypted_message)

        return decrypted_message
                
                
    def send_key(self, connection):
        if self.switch:
            return self.send_message(
                connection=connection,
                message=self.switch.decode(),
                send_pattern="!KEY:",
                receive_pattern="KEY_RECEIVED",
                timeout=5
            )


    def connection_handler(self, connection,username):
        if self.is_encrypted:
            self.send_key(connection)
      
        while not self.is_Server_Closed():
            time.sleep(0.03)
            
            message = connection.recv(1024).decode('utf-8')

            if self.is_encrypted:
                message = self.decrypted_message(message)

            self.logging.info(f"MESSAGE | {username}: {message}")

            failed_broadcast_users = self.broadcast_message(username, message)
            
            if failed_broadcast_users != []:
                self.logging.info(f"Message '{message}' broadcast failed for user '{failed_broadcast_users}'")


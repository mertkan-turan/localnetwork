import socket  
import logging
import sys
import time
from libraries.crypt_module import Crypto
import threading
import time

class Server:
    def __init__(self,port,username, is_encrypted=False):
        self.hostname=socket.gethostname()   
       
        #self.ip = "" #socket.gethostbyname_ex(socket.gethostname())[-1]
        self.ip = socket.gethostbyname(self.hostname).replace(",",".") 
        self.ip = "10.34.7.140"
        self.port = port
        self.connections = []
        self.logging=self.setup_logger()
        self.stop_event = threading.Event()  # Initialize stop_event
        self.is_encrypted = is_encrypted 
        self.crypto_module = None
        self.username = username
        self.switch = None
        self.clients = []  # List to store connected client sockets
        self.message_processing_mode = True
        self.lock = threading.Lock()  # Lock for managing shared data
        self.thread_pool = list()
        self.broadcast_message_buffer = list()

        if self.is_encrypted:
            self.crypto_module = Crypto()
            self.switch = self.crypto_module.create_key()
            self.crypto_module.create_cipher_suite()
             
    def init_threads(self):
        self.thread_pool.append( 
            threading.Thread(
                target=self.broadcast_message
            )
        )
        self.thread_pool[-1].start()

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
    
    def accept_connections(self):

        active_connections = {} 
        
        while True:
            
            conn = None
            try:
                conn, addr = self.server.accept()
                print("connnection accepted :" , conn , addr)
                if conn:
                    username = conn.recv(1024).decode('utf-8')  # Receive username from client
                    self.clients.append((conn, username))  # Store the new client socket
                    connection_thread = threading.Thread(
                        target=self.connection_handler,
                        args=(conn,username)
                    )
                    connection_thread.start()
                    active_connections[conn] = connection_thread  # Store the connection and its thread
                    self.logging.info(f"Connection accepted: {addr}")
                    
            except socket.timeout:
                self.logging.warn("Connection is waiting.. (Timeout)")
            except Exception as e:
                self.logging.error(f"Connection error: {e.args, e.__str__()}")
            
            # Clean  disconnected connections and their threads
            for conn, thread in active_connections.items():
                if not thread.is_alive():
                    del active_connections[conn]
                    self.remove_client(conn)  # Call a method to handle client removal
                    #self.clients.remove(conn)  # Remove the disconnected client socket
                    self.logging.info("Connection closed!")
    
    def remove_client(self, conn):
        for client in self.clients:
            if client[0] == conn:
                self.clients.remove(client)
                break
    
    def stop_server(self):
        self.server.close()
        self.logging.info("Server stopped.")
                          
                             
    def server_serve(self):
        self.logging.info(f"Server IP Address: {self.ip}")
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
       
        try:
            while not self.stop_event.is_set():
                
                # Example: Print a message every 8 seconds
                self.logging.debug("Server is running...")
                time.sleep(15)
                
        except KeyboardInterrupt:
                self.stop_event.set()
                self.logging.info("Server shutting down due to user interruption.")
                self.stop_server()

    # TODO: Fix
    
    def broadcast_message(self, sender, message):
        sender_username = None
        for client in self.clients:
            client_conn, username = client
            if client_conn == sender:
                sender_username = username
                break

        if sender_username:
            for client_conn, _ in self.clients:
                if client_conn != sender:
                    try:
                        client_conn.send(f"{sender_username}:{message}".encode())
                    except Exception as e:
                        self.logging.error(f"Error broadcasting message: {e.args, e.__str__()}")


   
    
    def decrypted_message(self, connection,username, encrypted_message):
 
        decrypted_message = ""        
        self.logging.info(f"Message received by {username} : {encrypted_message}")
        if self.is_encrypted and self.crypto_module:
            decrypted_message = self.crypto_module.decrypt_message(encrypted_message)
            if decrypted_message != "":
                self.logging.info(f"Decrypted message by {username} : {decrypted_message}")
                self.broadcast_message(connection, decrypted_message)  # Broadcast to other clients   
                
    def send_key(self, connection):
        key_pattern = "!KEY:"
        is_key_transmitted = False
        while not is_key_transmitted:
            self.logging.info("Sending key...")
            connection.send(key_pattern.encode())
            connection.send(self.switch)
            key_message = connection.recv(1024)

            if key_message.decode() == "KEY_RECEIVED":
                is_key_transmitted = True
                self.logging.info("Key Received by client!")
                        
    def connection_handler(self, connection,username):
        self.send_key(connection)
      
            # connection.sendall(key_pattern.encode() + self.switch)
        
        while True:
                encrypted_message = connection.recv(1024).decode('utf-8')
                if encrypted_message:
                    self.decrypted_message(connection,username, encrypted_message)
                    # Broadcast the decrypted message to all clients
                    self.broadcast_message(connection, encrypted_message)
                continue
               
                    
        
if __name__ == "__main__":
    
  

    ip_address = "10.34.7.129"  # Example IP address
    port = 12345  # Example port
    username = ""
    is_encrypted = True
    
    server = Server(port,username)
    server.create_server()
    server.server_serve()

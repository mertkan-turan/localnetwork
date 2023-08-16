import socket  
import logging
from libraries.crypt import Crypto
import pickle
from cryptography.fernet import Fernet

class Server:
    
        
    def __init__(self,port,username, is_encrypted=False):
        self.hostname=socket.gethostname()   
       
        #self.ip = "" #socket.gethostbyname_ex(socket.gethostname())[-1]
        self.ip = socket.gethostbyname(self.hostname).replace(",",".") 
        self.port = port
        self.connections = []
        self.logging=self.setup_logger()
        
        self.is_encrypted = is_encrypted 
        self.crypto_module = None
        self.keycik = None

        if self.is_encrypted:
            self.crypto_module = Crypto()
            self.keycik = self.crypto_module.create_key()
            
    def setup_logger(self):
        logger = logging.getLogger("ServerLogger")
        logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler('server_log.txt')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        return logger  
    
    def create_server(self):

        socket.setdefaulttimeout(40)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, int(self.port)))
        self.server.listen(5)

        return self.server

    def server_serve(self):
        print("Server IP Address:", self.ip)
        while True:
            conn = None
            try:
                conn, addr = self.server.accept()
                if conn:
                    self.connection_handler(conn)
                    self.logging.info("Connection accepted: %s", addr)
                   
            except socket.timeout:
                self.logging.info("Connection is waiting.. (Timeout)")
            except Exception as e:
                self.logging.error("Connection error: %s", e)
            finally:
                if conn:
                    conn.close()
                    self.logging.info("Connection closed!")
                    conn = None


    def connection_handler(self, connection):
        if self.is_encrypted:
            connection.sendall(self.keycik)  
        while True:
            encrypted_message = connection.recv(1024).decode("utf-8")
            print(f"Message received: {encrypted_message}")
            decrypted_message = ""
            if self.is_encrypted:
                decrypted_message = self.crypto_module.decrypt_message(encrypted_message)
                if decrypted_message != "":
                    print(f"Decrypted message: {decrypted_message}")

            
            
    def list_connections(self):
        results = ''
        
if __name__ == "__main__":

    ip_address = "10.34.7.129"  # Example IP address
    port = 12345  # Example port
    username = ""
    is_encrypted = True
    
    server = Server(port,username,is_encrypted)
    server.create_server()
    server.server_serve()
    
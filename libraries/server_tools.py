import socket  
import logging
import sys
from libraries.crypt_module import Crypto

class Server:
    def __init__(self,port,username, is_encrypted=False):
        self.hostname=socket.gethostname()   
       
        #self.ip = "" #socket.gethostbyname_ex(socket.gethostname())[-1]
        self.ip = socket.gethostbyname(self.hostname).replace(",",".") 
        self.ip = "10.34.7.141"
        self.port = port
        self.connections = []
        self.logging=self.setup_logger()
        
        self.is_encrypted = is_encrypted 
        self.crypto_module = None
        self.keycik = None

        if self.is_encrypted:
            self.crypto_module = Crypto()
            self.keycik = self.crypto_module.create_key()
            self.crypto_module.create_cipher_suite()
            print("Key Length: ", len(self.keycik))
            
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

        socket.setdefaulttimeout(15)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, int(self.port)))
        self.server.listen(5)
        # self.server.setblocking(False)

        return self.server

    def server_serve(self):
        self.logging.info(f"Server IP Address: {self.ip}")
        while True:
            conn = None
            try:
                conn, addr = self.server.accept()
                # self.logging.info(f"Waiting: {conn, addr}")
                if conn:
                    self.connection_handler(conn)
                    self.logging.info(f"Connection accepted: {addr}")
                   
            except socket.timeout:
                self.logging.warn("Connection is waiting.. (Timeout)")
            except Exception as e:
                self.logging.error(f"Connection error: {e.args, e.__str__()}")
            finally:
                if conn:
                    conn.close()
                    self.logging.info("Connection closed!")
                    conn = None


    def connection_handler(self, connection):
        if self.is_encrypted and self.keycik:
            key_pattern = "!KEY:"
            is_key_transmitted = False
            while not is_key_transmitted:
                self.logging.info("Sending key...")
                connection.send(key_pattern.encode())  
                connection.send(self.keycik)
                key_message = connection.recv(1024)
                
                if key_message.decode() == "KEY_RECEIVED":
                    is_key_transmitted = True
                    self.logging.info("Key Received by client!")
            # connection.sendall(key_pattern.encode() + self.keycik)
            
        while True:
            encrypted_message = connection.recv(1024).decode("utf-8")
            self.logging.info(f"Message received: {encrypted_message}")
            
            if self.is_encrypted and self.crypto_module:
                decrypted_message = self.crypto_module.decrypt_message(encrypted_message)
                if decrypted_message != "":
                    self.logging.info(f"Decrypted message: {decrypted_message}")


        
if __name__ == "__main__":

    ip_address = "10.34.7.129"  # Example IP address
    port = 12345  # Example port
    username = ""
    is_encrypted = True
    
    server = Server(port,username,is_encrypted)
    server.create_server()
    server.server_serve()
    
    
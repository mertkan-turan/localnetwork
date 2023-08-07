import socket  
import logging
class Server:
    
    def __init__(self,port):
        self.hostname=socket.gethostname()   
        self.ip = socket.gethostbyname(self.hostname).replace(",",".") 
        self.port = port
        self.connections = []

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
        socket.setdefaulttimeout(15)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("10.34.7.138", int(self.port)))
        self.server.listen(2)
        return self.server

    def server_serve(self):
        print("Server IP Address:", self.ip)
        self.setup_logger()
        while True:
            conn = None
            try:
                conn, addr = self.server.accept()
                if conn:
                    print("Connection accepted:", addr)
                    self.connection_handler(conn)
                    self.setup_logger.info("Connection accepted: %s", addr)
                    self.connection_handler(conn)
                   
            except socket.timeout:
                print("Connection is waiting.." +"(Timeout)")
                self.setup_logger.info("Connection is waiting.. (Timeout)")
            except Exception as e:
                print("Connection is waiting..", e) 
                self.setup_logger.error("Connection error: %s", e)
            finally:
                if conn:
                    conn.close()
                    print("Connection closed!")
                    self.setup_logger.info("Connection closed!")
                    conn = None


    def connection_handler(self,connection):
        while True:
            message = connection.recv(1024).decode("utf-8")
            if message != "":
                print(f"Message is {message}")
            
            
    def list_connections(self):
        results = ''
        
if __name__ == "__main__":
    ip_address = "10.34.7.129"  # Example IP address
    port = 12345  # Example port

    server = Server(port)
    server.create_server()
    server.server_serve()
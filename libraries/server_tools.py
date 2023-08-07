import socket  
class Server:
    
    def __init__(self,port):
        self.hostname=socket.gethostname()   
        self.ip = socket.gethostbyname(self.hostname).replace(",",".") 
        self.port = port
        self.connections = []

       
    
    def create_server(self):
<<<<<<< HEAD
        socket.setdefaulttimeout(25)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, int(self.port)))
        self.server.listen(5)
=======
        socket.setdefaulttimeout(35)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("localhost", int(self.port)))
        self.server.listen(2)
>>>>>>> 3659451 (Second)
        return self.server

    def server_serve(self):
        print("Server IP Address:", self.ip)
        while True:
            conn = None
            try:
                conn, addr = self.server.accept()
                if conn:
                    print("Connection accepted:", addr)
                   
                    self.connection_handler(conn)
            except socket.timeout:
                print("Connection is waiting.." +"(Timeout)")
            except Exception as e:
                print("Connection is waiting..", e) 
            finally:
                if conn:
                    conn.close()
                    print("Connection closed!")
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
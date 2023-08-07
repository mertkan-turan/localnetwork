import socket

class Server:
    
    def __init__(self,port):
        self.port = port
       
    
    def create_server(self):
        socket.setdefaulttimeout(15)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("10.34.7.129", int(self.port)))
        self.server.listen(2)
        return self.server

    def server_serve(self):
        while True:
            try:
                conn, addr = self.server.accept()
                if conn:
                    print("Connection accepted:", addr)
                    self.connection_handler(conn)
            except Exception as error:
                print("Connection is waiting..", error) 


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

  
  
  
 
import socket


def create_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(("127.0.0.1", int(port)))

    server.listen(100)

    def server_serve(self):
        while True:
            conn, addr = self.server.accept()
            print("Connection accepted:", addr)
            self.connection_handler(conn)


    def connection_handler(self,connection):
        while True:
            message = connection.recv(2048).decode("utf-8")
            if message != "":
                print(f"Message is {message}")
            
            
    def list_connections(self):
        results = ''
        
if __name__ == "__main__":
    ip_address = "127.0.0.1"  # Example IP address
    port = 12345  # Example port

    server = Server(port)
    server.create_server()
    server.server_serve()

  
  
  
 
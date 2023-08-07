import socket

class Client:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def connect(self, ip_address, port):
        self.client.connect((ip_address, int(port)))
        while True:
            message = input("Enter a message: ")
            self.client.sendall(message.encode())

if __name__ == "__main__":
    ip_address = "127.0.0.1"  # Example IP address
    port = 12345  # Example port

    client = Client()
    client.connect(ip_address, port)
import socket
import logging 

logging.basicConfig(filename='my_log.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Client:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Initialize the logging configuration
        logging.basicConfig(filename='client_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()
    def connect(self, ip_address, port):
        self.client.connect((ip_address, int(port)))
        while True:
            message = input("Enter a message: ")
            self.client.sendall(message.encode())
            logging.info(f"Message:{message}")

if __name__ == "__main__":
    ip_address = "127.0.0.1"  # Example IP address
    port = 12345  # Example port

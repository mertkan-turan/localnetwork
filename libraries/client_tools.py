import socket
<<<<<<< HEAD
import logging 

logging.basicConfig(filename='my_log.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
=======
import errno
>>>>>>> 3659451 (Second)

class Client:

    def __init__(self):
        socket.setdefaulttimeout(5)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def connect(self, ip_address, port):
<<<<<<< HEAD
        self.client.connect((ip_address, int(port)))
        while True:
            message = input("Enter a message: ")
            self.client.sendall(message.encode())
            logging.info(f"Message:{message}")

=======
        try:
            self.client.connect((ip_address, int(port)))
            while True:
                message = input("Enter a message: ")
                self.client.sendall(message.encode())
        except socket.timeout:
            print("Connection is waiting..")
            self.client.close()
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                print("Connection Refused.")
            else:
                print("Socket error.", e)
                print("Error message:", e.strerror)
            return False
        except Exception as e:
            print("Exception:", e)
            return False
    
        
>>>>>>> 3659451 (Second)
if __name__ == "__main__":
    ip_address = "127.0.0.1"  # Example IP address
    port = 12345  # Example port

    client = Client()
    client.connect(ip_address, port)

        
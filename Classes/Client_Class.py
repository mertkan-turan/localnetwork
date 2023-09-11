import threading
import time
import socket
from Classes.Socket_Interface_Class import COMMUNICATION_SIGNATURE, SocketInterface


class Client(SocketInterface):
    def __init__(self, ip, port, *args, **kwargs):
        super().__init__(port, *args, **kwargs)

        self.logger.info(
            f"Client initializing... Parameters are: {ip}, {port}"
        )
        
        self.thread_connection: threading.Thread

        self.ip = ip
        self.port = port  # The port where the client listens for incoming data
        
        self.create_socket(
            is_server=False,
        )
        self.logger.info(f"Client initialized at {ip}:{self.port}")
        
        
    def connect(self):
        self.logger.info(f"Client is connecting to {self.ip}:{self.port}")
        self.socket.connect((self.ip, self.port))
        self.logger.info(f"Client connected to {self.ip}:{self.port}")


    def connect_protocol(self):
        if self.is_encrypted:
            self.logger.info("Receiving key from server...")
            message_key = self.message_receive(
                self.socket,
                signature=COMMUNICATION_SIGNATURE.KEY,
                decrypt=False
            )
            if len(message_key) == 1:
                self.logger.info(f"Key received: {message_key[0]}")
                self.crypto_module.set_key(message_key[0])
                self.logger.info(f"Key setten.")
            else:
                self.logger.error(f"Key receiving failed. Received: {message_key}")
                self.socket.close()
                self.logger.info("Client closed.")
                exit(1)


    def connection_handler(self):
        try:
            self.connect_protocol()

        except Exception as e:
            self.logger.error(f"Connect Protocol Failed: {e}")
            self.socket.close()
            self.logger.info("Client closed.")
            exit(1)

        try:
            while True:
                message = input("Enter message: ")
                self.message_send(
                    self.socket,
                    message
                )
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard Interrupt detected. Closing client...")
            self.socket.close()
            self.logger.info("Client closed.")
            exit(0)
        except Exception as e:
            self.logger.error(f"Exception occurred in connection_handler: {e}")
            self.socket.close()
            self.logger.info("Client closed.")
            exit(1)

    def send_message(self, message):
        # Implement the logic to send the message here
        # For example, you might use sockets or another communication method
        # Replace this with your actual implementation
        print(f"Sending message to {self.ip}:{self.port}: {message}")
    def receive_data(self):
        # Create a server socket to listen for incoming data
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener_socket.bind(("0.0.0.0", self.port))
        self.logger.info(f"Client is listening on port {self.port}")

        while True:
            data, addr = listener_socket.recvfrom(1024)  # Adjust buffer size as needed
            self.logger.info(f"Received data from {addr}: {data.decode('utf-8')}")
        
    def broadcast_receiver(self):
        while True:
            try:
                message = self.message_receive(
                    self.socket
                )
                if len(message) > 1:
                    self.logger.info(f"Message received: {message}")
                else:
                    self.logger.error(f"Message receiving failed. Received: {message}")
            except KeyboardInterrupt:
                self.logger.info("Keyboard Interrupt detected. Closing client...")
                self.socket.close()
                self.logger.info("Client closed.")
                exit(0)
            except Exception as e:
                self.logger.error(f"Exception occurred in connection_handler: {e}")
                self.socket.close()
                self.logger.info("Client closed.")
                exit(1)


    def client_serve(self):
        self.logger.info("Client is serving...")
        self.connect()
        
        self.logger.info("Client is starting connection handler thread...")
        self.thread_connection = threading.Thread(
            target=self.connection_handler
        )
        self.thread_connection.start()
        
        self.logger.info("Client is starting broadcast receiver thread...")
        self.thread_broadcast_receiver = threading.Thread(
            target=self.broadcast_receiver
        )
        self.thread_broadcast_receiver.start()

        while True:
            time.sleep(1)
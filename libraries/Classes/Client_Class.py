
import errno
import threading
import socket
import time
from Libraries.Classes.Socket_Interface_Class import SocketInterface

class Client(SocketInterface):
    def __init__(self, port: int, username: str, is_encrypted: bool, is_server: bool, init_client=True, message_timeout_second: int=10, socket_timeout_second: int | None = None, logging_name: str = ""):
        super().__init__(port, username, is_encrypted, is_server, logging_name)
        
        self.message_timeout_second = message_timeout_second
        
        if init_client:
            self.create_socket(
                is_server=False, timeout_second=socket_timeout_second)
              
        self.init_threads()
        
    def init_threads(self):
        self.receive_thread = threading.Thread(target=self.task_receiver, daemon=True)
        self.send_thread = threading.Thread(target=self.task_sender, daemon=True)

    
    def start_threads(self):
        self.receive_thread.start()
        self.send_thread.start()
        
    def connect(self, ip_address, port):
        try:
            if not self.socket:
                self.logger.warning("Socket is not initialized! Automatically initializing...")
                self.create_socket(is_server=False)
                
            # Start a thread for receiving and displaying messages from the server
            self.socket.connect((ip_address, int(port)))
            # print("Connected to server: " + ip_address + ":" + str(port))
            
            if self.is_encrypted and self.crypto_module is not None:
                # Receive key from server
                self.logger.info("Receiving key from server...")
                # response, received_key = self.receive_messages(
                #     local_socket=self.socket, 
                #     pattern_received="!KEY:", 
                #     pattern_received_response="KEY_RECEIVED",
                #     decrypt=False,
                #     timeout=3 # TODO: DEBUG
                # )

                response, received_key = self.message_receiver(
                    local_socket=self.socket,
                    pattern_received="!KEY:",
                    pattern_received_response="KEY_RECEIVED",
                    timeout=self.message_timeout_second,
                    decrypt=False
                )
                
                
                if response:
                    self.logger.info("Key Received.")
                    self.crypto_module.set_key(received_key.encode())
                else:
                    self.logger.error(f"Key could not be received: {received_key}")
                    return -1

            self.logger.info("Sending username...")
            # response = self.send_message(
            #         local_socket = self.socket, 
            #         message = self.username,
            #         send_pattern = "!USERNAME:", 
            #         receive_pattern = "USERNAME_RECEIVED",
            #         timeout=3 # TODO: DEBUG
            # )
            
            response = self.message_sender(
                local_socket = self.socket, 
                message = self.username,
                send_pattern = "!USERNAME:", 
                receive_pattern = "USERNAME_RECEIVED",
                timeout=self.message_timeout_second
            )
            
            if response:
                self.logger.info(f"Username sent: {response}")
            
            self.logger.info("Successfully connected to server: %s:%s", ip_address, port)
            self.logger.info("If you want to exit the program, please write exit!!")

            self.start_threads()  # Start receiving and sending threads

        except socket.timeout:
            self.logger.warning("Connection timeout...")
            self.socket.close()
            return -2
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                self.logger.error("Connection Refused.")
            else:
                self.logger.error(f"Socket error: {e}")
                self.logger.error(f"Error message: {e.strerror}")
            return e.errno
        except Exception as e:
            self.logger.error(f"Exception: {e}")
            return -1
    
        return 0
    
    def task_receiver(self):
        while not self.is_Socket_Closed():
            time.sleep(0.1)
            try:
                # response, received_message = self.receive_messages(
                #     local_socket=self.socket,
                #     #pattern_received="!MESSAGE:",  # Adjust this pattern as needed
                #     #pattern_received_response="MESSAGE_RECEIVED"  # Adjust this pattern as needed
                # )
                response, received_message = self.message_receiver(
                    local_socket=self.socket,
                    # pattern_received="!KEY:",
                    # pattern_received_response="KEY_RECEIVED",
                    timeout=self.message_timeout_second,
                    decrypt=self.is_encrypted
                )
                if response and received_message:
                    # Process the decrypted message
                    # For example, you can print it or take some action based on the content
                    self.logger.info(f"Received message: {received_message}")

            except socket.timeout:
                self.logger.warning("Socket timeout while receiving.")
            except socket.error as e:
                self.logger.error("Socket error while receiving: %s", e)
            except Exception as e:
                self.logger.error("Exception while receiving: %s", e)

    def task_sender(self):
        while not self.is_Socket_Closed():
            time.sleep(0.1)
            message = input("Enter a message: ")
            
            self.action_control(message)
            
            # response = self.send_message(
            #     self.socket, 
            #     message
            # )

            response = self.message_sender(
                local_socket=self.socket,
                message=message,
                timeout=self.message_timeout_second
            )
            
            if response != 0:
                self.logger.error("Message can not be sent!")
    
    
    def action_control(self,message):
       if message.lower() == "exit":
            self.close_socket()
              
    def close_socket(self):
        self.set_Socket_Closed(shutdown=True)
        
        self.receive_thread.join()
        self.send_thread.join()
        
        self.socket.close()
        

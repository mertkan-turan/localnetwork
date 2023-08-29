
import threading
import socket
from Libraries.Classes.Socket_Interface_Class import SocketInterface


class Client(SocketInterface):
    def __init__(self, port: int, username: str, is_encrypted: bool, is_server: bool, init_client=True, logging_name: str = ""):
        super().__init__(port, username, is_encrypted, is_server, logging_name)
        
        self.receive_thread:threading.Thread
        
        if init_client:
            self.create_socket(is_server=False)
    
        self.init_threads()
        
    def init_threads(self):
        self.receive_thread = threading.Thread(
            target=self.receive_messages, 
            args=()
        )
        self.receive_thread.start()


    def connect(self, ip_address, port):
        try:
            # Start a thread for receiving and displaying messages from the server
            
            self.socket.connect((ip_address, int(port)))
            
            # Send username to server
            self.send_message(
                local_socket=self.socket, 
                message=self.username.encode('utf-8')
            )
            
            send_pattern = "!KEY:"
            pattern_receive = "KEY_RECEIVED"


            

            key_received = False
            while not key_received:
                key_pattern_message = self.client.recv(1024)
                # print("Key pattern message received:", key_pattern_message.decode())

                if key_pattern_message.decode() == "!KEY:":
                    while True:
                        key = self.client.recv(44)
                        if key != "":
                            key_received = True
                            self.client.sendall(key_pattern.encode())
                            break






            self.crypto_module.set_key(key)

            print("Successfully connected to server:", ip_address, ":", port)
            print("If you want to exit program,please write exit!! ")

            while True:
                message = input("Enter a message: ")

                encrypted_message = self.crypto_module.encrypt_message(message)
                self.client.sendall(encrypted_message)
                # self.client.sendall(message.encode())

                print(f"Sent to {ip_address} server: {message}")
                # self.receive_messages()

                # received_message = self.client.recv(1024).decode('utf-8')
                # sender_username, message = received_message.split(":", 1)  # Split sender_username and message
                # print(f"Received from {sender_username}: {message}")
                # print(f"Received from server  : {received_message}")
                # TODO: Fix
                if (message == "EXIT" or message == "Exit" or message == "exit"):
                    print("Are you sure you want to close the program? (Yes No)")
                    answer = input("Answer:")
                    if (answer == "Yes" or answer == "yes" or "YES"):
                        print("Program is closing..")
                        break
                    else:
                        continue
                else:
                    continue

        except socket.timeout:
            self.logger.warning("Connection is waiting...")
            self.client.close()
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                self.logger.error("Connection Refused.")
            else:
                self.logger.error("Socket error: %s", e)
                self.logger.error("Error message: %s", e.strerror)
            return False
        except Exception as e:
            self.logger.error("Exception: %s", e)
            return False
    

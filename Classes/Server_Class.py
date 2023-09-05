import logging
import sys
import threading
import time
from typing import List, Dict
from Classes.Socket_Interface_Class import COMMUNICATION_SIGNATURE, SocketInterface
import queue
from Libraries.Tools import tools



class Server(SocketInterface):
    def __init__(self, port, listen_number, timeout_second, *args, **kwargs):
        super().__init__(port, *args, **kwargs)
        
        self.logger.info(f"Server initializing... Parameters are: {port}, {listen_number}, {timeout_second}")
        
        self.thread_server: threading.Thread
        self.thread_broadcaster: threading.Thread
        
        self.broadcast_logger: logging.Logger
        self.create_broadcast_logger()

        self.template_thread_client: Dict = {
            "thread": None,
            "socket": None,
            "address": None
        }
        self.clients: Dict[
            str,
            Dict
        ] = dict()
        self.broadcast_queue: queue.Queue[tuple[str, str]] = queue.Queue()
        
        self.create_socket(
            is_server=True,
            listen_number=listen_number,
            timeout_second=timeout_second
        )
        self.logger.info(f"Server initialized on port {self.port}")


    def create_broadcast_logger(self):
        
        self.logger.debug(f"Creating broadcast logger...")
        self.broadcast_logger = logging.getLogger("broadcast_logger")
        self.broadcast_logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )

        self.logger.debug(f"Logger file is broadcast.log")
        file_handler = logging.FileHandler("broadcast.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        self.broadcast_logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)

        self.broadcast_logger.addHandler(stream_handler)
        self.logger.debug(f"Broadcast Logger created...")


    def server_serve(self):
        self.logger.info("Server is serving...")
        
        self.logger.info("Connection Accepter starting...")
        self.thread_server = threading.Thread(
            target=self.accept_connections
        )
        self.thread_server.start()
        
        self.logger.info("Broadcaster starting...")
        self.thread_broadcaster = threading.Thread(
            target=self.broadcaster
        )
        self.thread_broadcaster.start()
        
        
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Keyboard Interrupt detected. Closing server...")
            self.socket.close()
            self.logger.info("Server closed.")
            exit(0)
        except Exception as e:
            self.logger.error(f"Exception occurred at server_serve: {e}")
            self.socket.close()
            self.logger.info("Server closed.")
            exit(1)


    def accept_connections(self):
        while True:
            time.sleep(0.001)
            try:
                client_socket, address = self.socket.accept()
            except Exception as e:
                self.logger.debug(f"Exception occurred accept_connections: {e}")
                continue
            
            self.logger.info(f"Connection from {address} has been established!")
            
            self.clients[str(address)] = self.template_thread_client.copy()
            self.clients[str(address)]["socket"] = client_socket
            self.clients[str(address)]["address"] = address
            self.clients[str(address)]["thread"] = threading.Thread(
                target=self.handle_client,
                args=(address,)
            )
            self.clients[str(address)]["thread"].start()
            self.logger.info(f"Client {address} thread started!")


    def accept_protocol(self, local_socket):
        # Send Key if Encrypted Connection
        if self.is_encrypted:
            self.message_send(
                local_socket=local_socket,
                message=self.crypto_module.key,
                signature=COMMUNICATION_SIGNATURE.KEY,
                encrypt=False
            )


    def handle_client(self, address):
        self.accept_protocol(
            local_socket=self.clients[str(address)]["socket"]
        )
        while True:
            time.sleep(0.001)
            message = self.message_receive(
                self.clients[str(address)]["socket"]
            )
            if len(message) > 1:
                self.logger.error(f"Message received from {address} is broken: {message}")
            elif len(message) == 0:
                self.logger.info(f"Connection from {address} has been closed!")
                client = self.clients.pop(str(address))
                client["socket"].close()
                break
            else:
                self.logger.info(f"Message received from {address}: {message[0]}")
                self.broadcast_queue.put((address, message[0]))
                
                
    def broadcaster(self):
        self.logger.info("Broadcaster is serving...")
        
        while True:
            time.sleep(0.001)
            
            if not self.broadcast_queue.empty():
                broadcast_message = self.broadcast_queue.get()
                address, message = broadcast_message
                
                self.broadcast_logger.info(f"{address[0]} - {message}")
                
                self.logger.info(
                    f"Broadcasting message '{message}' from '{address}' to all clients."
                )
                
                for client in self.clients:
                    try:
                        if self.clients[client]["address"] == address:
                            continue
                        
                        self.message_send(
                            local_socket=self.clients[client]["socket"],
                            message=message,
                            signature=COMMUNICATION_SIGNATURE.MESSAGE,
                            encrypt=self.is_encrypted
                        )
                    except Exception as e:
                        self.logger.error(f"Exception occurred in broadcaster: {e}")
                        self.logger.info(f"Client {client} has been closed!")
                        self.clients[client]["socket"].close()
                        self.clients.pop(client)
                        continue

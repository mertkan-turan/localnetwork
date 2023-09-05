from copy import copy
from enum import Enum
import socket
import logging
import sys
import time
from typing import ByteString, List, Tuple
from Classes.Crypt_Class import Crypto
from abc import ABC
from Libraries.Tools.network_tools import get_ip



class SIGNATURES:
    TIMEOUT_PATTERN = "!*TIMEOUT*!"

    KEY_START_PATTERN = "!*KEY-START*!"
    KEY_END_PATTERN = "!*KEY-END*!"
    KEY_PATTERN_RESPONSE = "!*KEY_RECEIVED*!"

    ACTION_START_PATTERN = "!*ACTION-START*!"
    ACTION_END_PATTERN = "!*ACTION-END*!"
    ACTION_PATTERN_RESPONSE = "!*ACTION_RECEIVED*!"

    MESSAGE_START_PATTERN = "!*MESSAGE-START*!"
    MESSAGE_END_PATTERN = "!*MESSAGE-END*!"
    MESSAGE_PATTERN_RESPONSE = "!*MESSAGE_RECEIVED*!"


class SIGNATURE_TEMPLATE:
    MESSAGE_STRUCTURE = SIGNATURES.MESSAGE_START_PATTERN + "{}" + SIGNATURES.MESSAGE_END_PATTERN
    KEY_STRUCTURE = SIGNATURES.KEY_START_PATTERN + "{}" + SIGNATURES.KEY_END_PATTERN
    ACTION_STRUCTURE = SIGNATURES.ACTION_START_PATTERN + "{}" + SIGNATURES.ACTION_END_PATTERN


class COMMUNICATION_SIGNATURE(Enum):
    MESSAGE = 1
    KEY = 2
    ACTION = 3


class COMMUNICATION_STRUCTURE:
    STRUCTURES = {
        COMMUNICATION_SIGNATURE.MESSAGE: SIGNATURE_TEMPLATE.MESSAGE_STRUCTURE,
        COMMUNICATION_SIGNATURE.KEY: SIGNATURE_TEMPLATE.KEY_STRUCTURE,
        COMMUNICATION_SIGNATURE.ACTION: SIGNATURE_TEMPLATE.ACTION_STRUCTURE
    }
    
    @staticmethod
    def get(signature: COMMUNICATION_SIGNATURE):
        return COMMUNICATION_STRUCTURE.STRUCTURES[signature]
    
    @staticmethod
    def signature_check(signature: COMMUNICATION_SIGNATURE, message: str) -> Tuple[bool, bool]:
        start_flag, end_flag = False, False
        
        start, end = COMMUNICATION_STRUCTURE.STRUCTURES[signature].split(
            "{}", 
            maxsplit=1
        )

        if start in message:
            start_flag = True
        if end in message:
            end_flag = True
        
        return start_flag, end_flag

    @staticmethod
    def signature_add(message: str, signature: COMMUNICATION_SIGNATURE) -> str:
        return COMMUNICATION_STRUCTURE.STRUCTURES[signature].format(message)
        
    
    @staticmethod
    def signature_remove(message: str, signature: COMMUNICATION_SIGNATURE) -> str:
        start, end = COMMUNICATION_STRUCTURE.STRUCTURES[signature].split(
            "{}", 
            maxsplit=1
        )
        message_stripped_start = message.strip(start)
        message_stripped_end = message_stripped_start.strip(end)
        
        return message_stripped_end



class SocketInterface(ABC):
    def __init__(
        self, 
        port: int, 
        username: str, 
        is_encrypted: bool, 
        # is_server: bool, 
        message_max_byte_length:int=2048, 
        logging_name: str = ""
    ):
        self.socket: socket.socket
        self.crypto_module: Crypto

        self.ip_address = get_ip()
        self.logger = logging.getLogger(logging_name)
        
        self.configure_logger()

        self.logger.debug(
            f"SocketInterface Initializing for {logging_name}... Parameters are: {port, username, is_encrypted, message_max_byte_length}"
        )

        self.port: int = port
        self.username: str = username
        self.is_encrypted: bool = is_encrypted
        # self.is_server: bool = is_server
        self.message_max_byte_length: int = message_max_byte_length

        self.is_socket_closing: bool = False

        # Crypto Module Initialization
        if self.is_encrypted:
            self.logger.debug("Crypto Module Initializing...")
            self.crypto_module=Crypto()
            self.switch = self.crypto_module.create_key()
            self.crypto_module.create_cipher_suite()
            self.logger.debug(f"Crypto Module Key: {self.switch}")


    ##################
    ### PROPERTIES ###
    ##################

    @property
    def is_Socket_Closed(self):
        return self.is_socket_closing


    @is_Socket_Closed.setter
    def is_Socket_Closed(self, shutdown: bool):
        self.is_socket_closing = shutdown


    @property
    def ip_address(self):
        return self.__ip

    @ip_address.setter
    def ip_address(self, ip_address: str):
        self.__ip = ip_address


    #######################
    #### CLASS METHODS ####
    #######################

    def create_socket(self, is_server: bool, listen_number=-1, timeout_second: int | None = None):
        self.logger.debug(f"Socket Creating... Parameters are: {is_server, listen_number, timeout_second}")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(timeout_second)
        # self.socket.setblocking(False)

        if is_server == True:
            self.socket.bind((self.ip_address, self.port))
            if listen_number != -1:
                self.socket.listen(listen_number)
        self.logger.debug(f"Socket created.")


    def configure_logger(self):
        self.logger.debug(f"Logger Configuring...")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        self.logger.debug(f"Logger file is {self.logger.name}.log")
        file_handler = logging.FileHandler(self.logger.name + ".log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(stream_handler)
        self.logger.debug(f"Logger configured.")


    def close_socket(self):
        self.logger.debug(f"Socket closing...")
        self.socket.close()
        self.logger.debug(f"Socket closed.")


    #######################
    ### MESSAGE PACKING ###
    #######################

    def __message_pack_str(self, message: str, message_max_len: int) -> List[str]:
        self.logger.debug(f"Message str packing... Parameters are: {message, message_max_len}")
        message_pack: List[str] = list()
        message_len:int = len(message)
        
        if message_len > message_max_len:
            steps = int(message_len / message_max_len)
            for i in range(steps):
                message_pack.append(message[i * message_max_len: (i + 1) * message_max_len])
        else:
            message_pack.append(message)
            
        # Last message conversion and packing
        message_pack[-1] = (message_pack[-1] + "\0" * message_max_len)[:message_max_len]
        self.logger.debug(f"Message str packed: {message_pack}")
        return message_pack

    def message_pack(self, message: str, message_max_len: int, signature: COMMUNICATION_SIGNATURE) -> List[bytes]:

        self.logger.debug(
            f"Message byte packing... Parameters are: {message, message_max_len}"
        )

        # Re-Formatting Message with Message Structure
        temp_message_structure = COMMUNICATION_STRUCTURE.signature_add(
            message,
            signature
        )
        temp_message_structure_byte = temp_message_structure.encode()
        
        # Message Packing
        message_pack: List[bytes] = list()
        message_len: int = len(temp_message_structure_byte)
        
        if message_len > message_max_len:
            steps = int(message_len / message_max_len)
            for i in range(steps):
                message_pack.append(
                    temp_message_structure_byte[
                        i * message_max_len: 
                        (i + 1) * message_max_len
                    ]
                )
        else:
            message_pack.append(temp_message_structure_byte)
            
        # Last message conversion and packing
        last_message_converted = bytes(message_pack[-1])
        last_message_converted = last_message_converted.decode()
        last_message_converted += "\0" * \
            (self.message_max_byte_length - len(last_message_converted))
        message_pack[-1] = last_message_converted[:message_max_len].encode()
                        
        self.logger.debug(f"Message byte packed: {message_pack}")
        return message_pack


    def message_unpack(self, message_pack: List[str], signature: COMMUNICATION_SIGNATURE) -> str:
        self.logger.debug(
            f"Message un-packing... Parameters are: {message_pack}"
        )

        message_pack[-1] = message_pack[-1].strip("\0")
        self.logger.debug(
            f"Message stripped: {message_pack}"
        )
        message_pack[0] = COMMUNICATION_STRUCTURE.signature_remove(
            message_pack[0],
            signature
        )
        self.logger.debug(
            f"Message start signature removed: {message_pack}"
        )
        message_pack[-1] = COMMUNICATION_STRUCTURE.signature_remove(
            message_pack[-1],
            signature
        )
        self.logger.debug(
            f"Message end signature removed: {message_pack}"
        )

        message_str = "".join(message_pack)
        
        self.logger.debug(f"Message un-packed: {message_str}")
        return message_str


    ###########################
    ### MESSAGE PRE-ACTIONS ###
    ###########################

    ### MESSAGE SEND PRE-ACTIONS ###

    def message_send_pre_actions(self, message: str, encrypt: bool = True, signature: COMMUNICATION_SIGNATURE = COMMUNICATION_SIGNATURE.MESSAGE) -> List[bytes | ByteString]:
        self.logger.debug(
            f"Message send byte pre-actions... Parameters are: {message, encrypt, signature}"
        )

        if self.is_encrypted and encrypt:
            message_encrypted = self.crypto_module.encrypt_message(
                message
            )
            message_str = bytes(message_encrypted).decode()
        else:
            message_str = copy(message)
        
        message_package_byte = self.message_pack(
            message=message_str,
            message_max_len=self.message_max_byte_length,
            signature=signature
        )

        self.logger.debug(f"Message send byte pre-actions: {message_package_byte}")
        return message_package_byte


    ### MESSAGE RECEIVE PRE-ACTIONS ###

    def message_receive_pre_actions(self, message_pack: List[str], signature: COMMUNICATION_SIGNATURE, decrypt: bool = True) -> str:
        self.logger.debug(f"Message receive pre-actions... Parameters are: {message_pack, decrypt}")
        
        # Last message un-packing
        message_unpacked = self.message_unpack(message_pack, signature)
        
        # Message Decryption
        if self.is_encrypted and decrypt:
            self.logger.debug(f"Decrypting Message: {message_unpacked}")
            message_plain = self.crypto_module.decrypt_message(
                message_unpacked
            )
        else:
            self.logger.debug(f"No Decryption: {message_unpacked}")
            message_plain = copy(message_unpacked)
        
        self.logger.debug(f"Message receive pre-actions: {message_plain}")
        return message_plain
    
    
    ######################
    ### SOCKET ACTIONS ###
    ######################
    
    
    ### MESSAGE RECEIVE ###
    
    def message_receive(self, local_socket: socket.socket, sleep_time: float = 0., signature: COMMUNICATION_SIGNATURE = COMMUNICATION_SIGNATURE.MESSAGE, decrypt:bool=True) -> List[str]:
        self.logger.debug(
            f"Receive started... Parameters are: {local_socket, sleep_time, signature, decrypt}"
        )
        
        receiver_pack:List[str] = list()
        
        while True:
            if sleep_time > 0.:
                time.sleep(sleep_time)
                
            received_byte = local_socket.recv(self.message_max_byte_length)
            
            if received_byte != b"":
                received_str = received_byte.decode()
                
                receiver_pack.append(received_str)
                
                signature_start, signature_end = COMMUNICATION_STRUCTURE.signature_check(
                    signature=signature,
                    message=received_str
                )
                self.logger.debug(f"Signature check: {signature_start, signature_end} | Message: {received_str}")
                
                if signature_start:
                    self.logger.debug(f"Message start signature received.")
                               
                if signature_end:
                    self.logger.debug(f"Message end signature received.")
                    received_message_plain = self.message_receive_pre_actions(
                        message_pack=receiver_pack,
                        decrypt=decrypt,
                        signature=signature
                    )
                    self.logger.debug(f"Received message: {received_message_plain}")
                    self.logger.debug(f"Receive ended.")
                    return [received_message_plain]
                
                time.sleep(sleep_time)
            else:
                self.logger.debug(f"Socket closed by remote host.")
                break
        
        self.logger.debug(f"Receive ended with failure.")
        return receiver_pack
    
    
    ### MESSAGE SEND ###

    def message_send(self, local_socket: socket.socket, message: str, sleep_time: float = 0., encrypt:bool=True, signature: COMMUNICATION_SIGNATURE = COMMUNICATION_SIGNATURE.MESSAGE):
        self.logger.debug(f"Send started... Parameters are: {local_socket, message, sleep_time, encrypt, signature}")
        
        message_pack = self.message_send_pre_actions(
            message=message,
            signature=signature,
            encrypt=encrypt
        )
        
        for message_byte in message_pack:
            local_socket.sendall(message_byte)
            if sleep_time > 0.:
                time.sleep(sleep_time)
        
        self.logger.debug(f"Send ended.")





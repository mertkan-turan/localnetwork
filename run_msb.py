from Libraries.Tools.network_tools import get_ip
from Classes.Client_Class import Client
from Classes.Server_Class import Server

if __name__ == "__main__":
    
    message_max_byte_length = input("Max Message Length [Default is 1024]: ")
    if message_max_byte_length == "" or not message_max_byte_length.isnumeric():
        message_max_byte_length = 1024
    else:
        message_max_byte_length = int(message_max_byte_length)
        
    is_server = True if input("Is Server (y/n): ") == "y" else False
    is_encrypted = True if input("Is Encrypted (y/n): ") == "y" else False
    
    if is_server:
        server = Server(
            username="socket_server",
            is_encrypted=is_encrypted,
            port=5000,
            listen_number=5,
            timeout_second=5,
            logging_name="socket_server",
            message_max_byte_length=message_max_byte_length
        )
        server.server_serve()
    else:
        client = Client(
            username="socket_client",
            is_encrypted=is_encrypted,
            ip=get_ip(),
            port=5000,
            logging_name="socket_client",
            message_max_byte_length=message_max_byte_length
        )
        client.client_serve()

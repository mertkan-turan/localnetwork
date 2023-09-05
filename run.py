from Libraries.Tools import cli_tools
from Libraries.others import Client2_Class
from Libraries.others import Server2_Class



if __name__ == "__main__": 
    is_server,is_encrypted, (ip, port, username) = cli_tools.main_actions()
    
    if is_server == True :
        server_object = Server2_Class.Server(
            port=int(port),
            username=username, 
            is_encrypted=is_encrypted,
            init_server=True,
            listen_number=10,
            socket_timeout_second=25,
            logging_name="server"
        )
        #server_object.socket.listen(-1)
        server_object.server_serve()
    else:
        client_object = Client2_Class.Client(
            port=int(port),
            username=username,
            is_encrypted=is_encrypted,
            is_server=False,
            init_client=True,
            message_timeout_second=10,
            socket_timeout_second=25,
            logging_name="client"
        )
        client_object.connect(ip, port)
        
        
        
        
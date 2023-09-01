from Libraries.Tools import cli_tools
from Libraries.Classes import Client_Class
from Libraries.Classes import Server_Class



if __name__ == "__main__": 
    is_server,is_encrypted, (ip, port, username) = cli_tools.main_actions()
    
    if is_server == True :
        server_object = Server_Class.Server(
            port=int(port),
            username=username, 
            is_encrypted=is_encrypted,
            init_server=True,
            listen_number=10,
            timeout_second=9999,
            logging_name="server"
        )
        #server_object.socket.listen(-1)
        server_object.server_serve()
    else:
        client_object = Client_Class.Client(
            port=int(port),
            username=username,
            is_encrypted=is_encrypted,
            is_server=False,
            init_client=True,
            timeout_second=9999,
            logging_name="client"
        )
        client_object.connect(ip, port)
        
        
        
        
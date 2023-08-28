from Libraries.Tools import tools
from Libraries.Tools import cli_tools
from Libraries.Classes import Client_Class_Old
from Libraries.Tools import cli_tools
from Libraries.Classes import Server_Class


if __name__ == "__main__": 
    ip, port, username = cli_tools.main_actions()
    server_object = Server_Class.Server(
        port=int(port),
        username=username, 
        is_encrypted=True,
        init_server=True,
        logging_name="alfa"
    )

    server_object.server_serve()
    
    ip, port, username = cli_tools.main_actions()
    json_data = tools.usage_info(ip,port,username)
    Client_Class_Old = Client_Class_Old.Client(username)
    Client_Class_Old.connect(ip, port)

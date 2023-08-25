from Libraries.Tools import cli_tools
from Libraries.Classes import Server_Class


if __name__ == "__main__": 
    print ()
    ip, port, username = cli_tools.main_actions()
    server_object = Server_Class.Server(
        port=int(port),
        username=username, 
        is_encrypted=True,
        init_server=True
    )

    server_object.server_serve()
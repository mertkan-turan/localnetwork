import json
from Libraries.Tools import tools
from Libraries.Tools import cli_tools
from Libraries.Classes import client
from Libraries.Tools import cli_tools
from Libraries.Classes import server


if __name__ == "__main__": 
    print ()
    ip, port, username = cli_tools.main_actions()
    server_object = server.Server(
        port=int(port),
        username=username, 
        is_encrypted=True,
        init_server=True
    )

    server_object.server_serve()
    
    ip, port, username = cli_tools.main_actions()
    json_data = tools.usage_info(ip,port,username)
    client = client.Client(username)
    client.connect(ip, port)

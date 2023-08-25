import json
from Libraries.Tools import tools
from Libraries.Tools import cli_tools
from Libraries.Classes.Client_Class_Old import Client


if __name__ == "__main__":
    ip, port, username = cli_tools.main_actions()
    json_data = tools.usage_info(ip,port,username)
    client = Client(username)
    client.connect(ip, port)

    
   
    
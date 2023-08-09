import json
from libraries import tools
from libraries import cli_tools
from libraries import client_tools


if __name__ == "__main__":
    ip, port, username = cli_tools.main_actions()
    json_data = tools.usage_info(ip,port,username)
    client = client_tools.Client()
    client.connect(ip, port)

    
   
    
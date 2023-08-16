
from pathlib import Path
import json
import logging
from libraries import tools
#Merhaba
def main_actions():
    device_type = int(input("Is this device client [0] or server [1]:"))
    
    if device_type == 1:
        return main_actions_server()
    else: 
        return main_actions_client()
    
    
        
def main_actions_client():
    
    tools.write_configuration(overwrite=False) 
    json_data = tools.read_configuration()
    username = input(f"Enter Username [Old:{json_data['username']}]: ")
    if(username == ""):
        username = json_data['username']
    server_ip = input("Enter IP:")
    if(server_ip == ""):
        server_ip = json_data['ip']
    port = input("Enter Port:")
    if(port == ""):
        port = json_data['port']
        
    tools.write_configuration(ip=server_ip,port=port,username=username,overwrite=True)
    
    return  server_ip, port, username

def main_actions_server():
    username = input("Enter Username: ")
    port = input("Enter Port:")
    ip = ""

    return ip, port, username





from Libraries.Tools import tools


def main_actions() -> tuple[bool, bool, tuple[str, str, str]]:
    device_type = input("Is this device server? (yes/no): ").lower() == "yes"
    is_encrypted = input("Is encryption enabled? (yes/no): ").lower() == "yes"
    if device_type == "yes":
        return device_type,is_encrypted,main_actions_server()
    else: 
        return device_type,is_encrypted,main_actions_client()
    
    
        
def main_actions_client():
    
    tools.write_configuration(overwrite=False) 
    json_data = tools.read_configuration()
    username = input(f"Enter Username [Old:{json_data['username']}]: ")
    if(username == ""):
        username = json_data['username']
    server_ip = input(f"Enter IP [Old:{json_data['ip']}]: ")
    if(server_ip == ""):
        server_ip = json_data['ip']
    port = input(f"Enter Port [Old:{json_data['port']}]: ")
    if(port == ""):
        port = json_data['port']
        
    tools.write_configuration(ip=server_ip,port=port,username=username,overwrite=True)
    
    return  server_ip, port, username

def main_actions_server() -> tuple[str, str, str]:
    username = input("Enter Username: ")
    port = input("Enter Port:")
    ip = ""
    

    return ip, port, username




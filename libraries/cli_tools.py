
def main_actions():
    device_type = int(input("Is this device client [0] or server [1]:"))
    if device_type == 1:
        return main_actions_server()
    else: 
        return main_actions_client()
    

def main_actions_client():
    ip = input("Enter IP:")
    port = input("Enter Port:")
    
    return  ip, port 

def main_actions_server():
    port = input("Enter Port:")
    ip = ""

    return ip, port 
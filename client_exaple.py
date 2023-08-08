import json
from libraries import cli_tools
from libraries import client_tools

def create_json(ip,port):
        if ip and port:
            data = {
                "ip": ip,
                "port": port
            }
            return data
        else:
            return None
        
if __name__ == "__main__":
    ip, port = cli_tools.main_actions()

    client = client_tools.Client()
    client.connect(ip, port)
    json_data = create_json(ip,port)
    
    json_file_path = 'C:\\Users\\m.said.bilgehan\\Workspace\\mylocalnetwork\\json_data.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)  
    print(json_data)
   
    
import json
from pathlib import Path

def usage_info(ip="",port="",username=""):
        data = {
            "ip": ip,
            "port": port,
            "username": username
        }
        return data

def write_configuration(file_path="settings.conf", ip="",port="",username="", overwrite=False):
    file_path = "settings.conf"
    app_root_path = "/".join(__file__.split("\\")[:-1])
    
    
    #print("app_root_path", app_root_path)
    #print(__file__)
    #app_root_path = __file__[:__file__.rfind("\\")]

    if overwrite:
        with open(app_root_path + "/" + file_path, 'w') as json_file:
            json.dump(usage_info(ip,port,username),json_file) 
    else:
        config_path_object = Path(app_root_path + "/" + file_path)
        if config_path_object.is_file():
            pass
        else:
            with open(app_root_path + "/" + file_path, 'w') as json_file:
                json.dump(usage_info(ip,port,username),json_file)
            
    
    
def read_configuration(file_path = "settings.conf"):
    
    #print(__file__)
    #print( __file__.split('\\')) 
    #print( __file__.split('\\')[:-1])
    #print( "\\".join(__file__.split('\\')[:-1]))
    app_root_path = "/".join(__file__.split("\\")[:-1])
    
    with open(app_root_path + "/" + file_path, 'r') as json_file:
       config = json.load(json_file)
    
    return config

    

    
    
    
    
  

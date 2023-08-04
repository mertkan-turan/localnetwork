import socket
from concurrent.futures import ThreadPoolExecutor

def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        res=sock.connect_ex ((ip,port)) 

        if res == 0:
            print (f"{ip}:{port} open")   
        else : 
            print(f"{ip}:{port} closed") 
         
        sock.close()

        
    except Exception as e:
        print(f"Error occurred while scanning port {port} on IP {ip}: {e}")

ports_to_scan = [5005]

with ThreadPoolExecutor(max_workers=20) as executor:
  
        for ip_suffix in range(0, 255):  
            ip = f"10.34.7.{ip_suffix}"

            for port in ports_to_scan:
                executor.submit(scan_port, ip, port)



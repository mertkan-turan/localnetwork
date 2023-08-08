import socket
from concurrent.futures import ThreadPoolExecutor

def scan_port(ip, port): # We define the function to be used to scan a single port.
    try:
     
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # We create a socket (using the IPv4 family and TCP protocol).

        res=sock.connect_ex ((ip,port)) # We are trying to connect on the specified IP and port.

        if res == 0:
            print (f"{ip}:{port} open")   
        else : 
            print(f"{ip}:{port} closed") 
         
        sock.close()

        
    except Exception as e:
        print(f"Error occurred while scanning port {port} on IP {ip}: {e}")

ports_to_scan = [5005]

with ThreadPoolExecutor(max_workers=20) as executor:
  
        for ip_suffix in range(0, 255): # to return 0-255
            ip = f"10.34.7.{ip_suffix}" # We generate the full IP address.

            for port in ports_to_scan:
                executor.submit(scan_port, ip, port)



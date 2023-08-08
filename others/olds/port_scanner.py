import socket
from concurrent.futures import ThreadPoolExecutor

def scan_port(ip, port):
    try:
        # Specify IP version and type to create socket (IPv4 and TCP)
        # The socket is created with AF_INET (IPv4) and SOCK_STREAM (TCP).
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

       # Set a timeout of 1 second (optional, for processing time).
        sock.settimeout(5)

       # Try to connect to the specified IP address and port number.
        print(f"Scanning {ip}:{port}")
        result = sock.connect_ex((ip, port))
       # Returns 0 if the connection is successful (port is open).
        if result == 0:
            print(f"Port {port} açık.")
        
        
        sock.close()
        

    except socket.error:
       # It drops here in error situations (port closed or target device unreachable).
        pass

# Determine the IP addresses of the devices in your local network.
local_network_ips = ['10.34.7.']

# Specify the port numbers you want to scan.
ports_to_scan = [5005]  # As an example, let's scan ports 80, 443, 22 and 3389.

# Parallel scanning using ThreadPoolExecutor.
with ThreadPoolExecutor(max_workers=20) as executor:
    for ip in local_network_ips:
        for port in ports_to_scan:
            executor.submit(scan_port, ip, port)

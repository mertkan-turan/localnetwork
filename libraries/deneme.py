import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("10.34.7.138", 80))
print(s.getsockname()[0])
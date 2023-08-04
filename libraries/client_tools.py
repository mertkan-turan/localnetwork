import socket


def create_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    return client


def client_connect(client, ip_address, port):
    client.connect((ip_address, int(port)))
    while True:
        message = input("Enter a message: ")
        client.sendall(message.encode())


            
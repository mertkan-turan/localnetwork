import socket


def create_server(ip_address, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((ip_address, int(port)))

    server.listen(100)

    return server

def main_chit_chat(server):
    while True:
        conn, addr = server.accept()
        client_handler(conn)


def client_handler(connection):
    message = connection.recv(2048).decode("utf-8")

    while True:
        if message != "":
            print(f"Mesage is {message}")
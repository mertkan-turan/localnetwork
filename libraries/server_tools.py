import socket


def create_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(("127.0.0.1", int(port)))

    server.listen(100)

    return server

def server_serve(server):
    conn, addr = server.accept()
    print("Connection accepted:", addr)
    connection_handler(conn)


def connection_handler(connection):
    while True:
        message = connection.recv(1024).decode("utf-8")
        if message != "":
            print(f"Message is {message}")
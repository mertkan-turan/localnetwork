from libraries import cli_tools
from libraries import server_tools


if __name__ == "__main__":
    ip, port, username = cli_tools.main_actions()
    server = server_tools.Server(port,username)
    server.create_server()
    server.server_serve()
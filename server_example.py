from libraries import cli_tools
from libraries import server_tools


if __name__ == "__main__":
    username, ip, port = cli_tools.main_actions()
    server = server_tools.Server(port)
    server.create_server()
    server.server_serve()
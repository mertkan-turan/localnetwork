from libraries import cli_tools
from libraries import server_tools


if __name__ == "__main__":
    username, ip, port = cli_tools.main_actions()

    server = server_tools.create_server(ip, port)
    server_tools.main_chit_chat(server)
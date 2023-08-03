from libraries import cli_tools
from libraries import networking_tools


if __name__ == "__main__":
    username, ip, port = cli_tools.main_actions()

    server = networking_tools.create_server(ip, port)
    networking_tools.main_chit_chat(server)
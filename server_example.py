from libraries import cli_tools
from libraries import server_tools


if __name__ == "__main__":
    ip, port, username = cli_tools.main_actions()
    server_object = server_tools.Server(
        port=int(port),
        username=username, 
        is_encrypted=True,
        init_server=True
    )

    server_object.server_serve()
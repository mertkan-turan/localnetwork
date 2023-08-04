from libraries import cli_tools
from libraries import client_tools


if __name__ == "__main__":
    username, ip, port = cli_tools.main_actions()

    client = client_tools.create_client()
    client_tools.client_connect(client, ip, port)
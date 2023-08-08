from libraries import cli_tools
from libraries import client_tools


if __name__ == "__main__":
    ip, port = cli_tools.main_actions()

    client = client_tools.Client()
    client.connect(ip, port)
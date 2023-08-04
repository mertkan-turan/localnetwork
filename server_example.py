import logging
from libraries import cli_tools
from libraries import server_tools


if __name__ == "__main__":
    username, ip, port = cli_tools.main_actions()

    server = server_tools.create_server(port)
    server_tools.server_serve(server)


"""Logging""" 
logging.basicConfig(filename="socket.server.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s") 

logging.info('Server listening on localhost:12345')

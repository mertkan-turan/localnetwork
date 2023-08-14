import socket
import pickle
from cryptography.fernet import Fernet

# key = Fernet.generate_key()

with open("./key", "rb") as key_file:
    key = pickle.load(key_file)

cipher_suite = Fernet(key)


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect(("127.0.0.1", 1234))

def mesaj_gonder(mesaj):
    sifrelenmis_mesaj = cipher_suite.encrypt(mesaj.encode())
    client_socket.send(sifrelenmis_mesaj)

def mesaj_al():
    sifrelenmis_mesaj = client_socket.recv(1024)
    desifrelenmis_mesaj = cipher_suite.decrypt(sifrelenmis_mesaj).decode()
    return desifrelenmis_mesaj

while True:
    giden_mesaj = input("Server: ")
    mesaj_gonder(giden_mesaj)
    

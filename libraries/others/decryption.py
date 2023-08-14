import socket
import pickle
from cryptography.fernet import Fernet

# key = Fernet.generate_key()

with open("./key", "rb") as key_file:
    key = pickle.load(key_file)

cipher_suite = Fernet(key)

HOST = '127.0.0.1'
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print("Bağlantı bekleniyor...")
client_socket, client_address = server_socket.accept()
print("Bağlandı:", client_address)


def mesaj_al():
    sifrelenmis_mesaj = client_socket.recv(1024)
    desifrelenmis_mesaj = cipher_suite.decrypt(sifrelenmis_mesaj).decode()
    return desifrelenmis_mesaj

while True:
    gelen_mesaj = mesaj_al()
    print("User:", gelen_mesaj)
    

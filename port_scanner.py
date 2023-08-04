import socket
from concurrent.futures import ThreadPoolExecutor

def scan_port(ip, port):
    try:
        # Soket oluşturmak için IP versiyonunu ve türünü belirleyin (IPv4 ve TCP)
        # Soket, AF_INET (IPv4) ve SOCK_STREAM (TCP) ile oluşturulur.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 1 saniyelik bir zaman aşımı belirleyin (opsiyonel, işlem süresi için).
        sock.settimeout(5)

        # Belirtilen IP adresi ve port numarasına bağlanmaya çalışın.
        print(f"Scanning {ip}:{port}")
        result = sock.connect_ex((ip, port))

        # Eğer bağlantı başarılıysa (port açıksa) 0 döner.
        if result == 0:
            print(f"Port {port} açık.")
        
        # Soketi kapatmayı unutmayın.
        sock.close()

    except socket.error:
        # Hata durumlarında (port kapalı veya hedef cihaza ulaşılamıyor) buraya düşer.
        pass

# Yerel ağınızdaki cihazların IP adreslerini belirleyin.
local_network_ips = ['10.34.7.']

# Taramak istediğiniz port numaralarını belirleyin.
ports_to_scan = [5005]  # Örnek olarak 80, 443, 22 ve 3389 numaralı portları tarayalım.

# ThreadPoolExecutor kullanarak taramayı paralel hale getirin.
with ThreadPoolExecutor(max_workers=20) as executor:
    for ip in local_network_ips:
        for port in ports_to_scan:
            executor.submit(scan_port, ip, port)

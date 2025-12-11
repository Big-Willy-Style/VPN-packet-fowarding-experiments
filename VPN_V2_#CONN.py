#simple VPN Proxy Server Implementation has connect and HTTP forwarding
#DO NOT USE ON A PUBLIC NETWORK IT IS NOT SECURE ENOUGH!!!!!!!!!!!!!!!!!!!!!!
#however can use https sites with the CONNECT method the only advanatge of this over V1 is that it can handle https sites


import threading
import socket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

proxy_host = '127.0.0.1'
proxy_port = 8888


def forward_data(source, destination):
    """Forward bytes from one socket to another until closed."""
    try:
        while True:
            data = source.recv(4096)
            if not data:
                break
            destination.sendall(data)
    except Exception as e:
        logger.error(f"Forwarding error: {e}")
    finally:
        source.close()
        destination.close()


def handle_client(client_socket):
    try:
        #read first request
        request = client_socket.recv(4096).decode("utf-8", errors="ignore")

        if request.startswith("CONNECT"):
            host_port = request.split(" ")[1]
            target_host, target_port = host_port.split(":")
            target_port = int(target_port)

            logger.info(f"HTTPS CONNECT to {target_host}:{target_port}")

            #conn to target server
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((target_host, target_port))

            #tell browser the tunnel is ready
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            #daata fowarding
            threading.Thread(target=forward_data, args=(client_socket, remote)).start()
            threading.Thread(target=forward_data, args=(remote, client_socket)).start()

        else:
            #HTTP requests
            first_line = request.split("\r\n")[0]
            logger.info(f"HTTP request: {first_line}")

            #extract the host from headers
            headers = request.split("\r\n")
            host_line = next(h for h in headers if h.lower().startswith("host:"))
            host = host_line.split(":", 1)[1].strip()

            #standard ports
            if ":" in host:
                target_host, target_port = host.split(":")
                target_port = int(target_port)
            else:
                target_host = host
                target_port = 80

            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((target_host, target_port))

            remote.sendall(request.encode())

            #data fowarding cli
            while True:
                data = remote.recv(4096)
                if not data:
                    break
                client_socket.sendall(data)

            remote.close()
            client_socket.close()

    except Exception as e:
        logger.error(f"Error handling client: {e}")
        client_socket.close()


def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((proxy_host, proxy_port))
    server.listen(100)
    logger.info(f"Proxy listening on {proxy_host}:{proxy_port}")

    while True:
        client_socket, addr = server.accept()
        logger.info(f"Accepted connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_proxy()

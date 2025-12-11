#simple VPN Proxy Server Implementation
#DO NOT USE ON A PUBLIC NETWORK IT IS NOT SECURE ENOUGH!!!!!!!!!!!!!!!!!!!!!!


import threading
import socket
import logging

# log config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#proxy sever config
proxy_host = '127.0.0.1'
proxy_port = 8888

# target server config
target_host = 'neverssl.com'
target_port = 80

def handle_client(client_socket):
    #conn
    try:
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect((target_host, target_port))#
    except Exception as e:
        logger.error(f"Failed to connect to target server: {e}")
        client_socket.close()
        return
    
    #data forwarding
    try:
        while True:
            request = client_socket.recv(4096)
            if not request:
                break

            if len(request):
                logger.info(f"Forwarding {len(request)} bytes to target server")
                target_socket.send(request)
            else:
                break

            response = target_socket.recv(4096)
            if len(response):
                logger.info(f"Forwarding {len(response)} bytes to client")
                client_socket.send(response)
            else:
                break
    except Exception as e:
        logger.error(f"Error during data forwarding: {e}")
    
    #cleanup
    client_socket.close()
    target_socket.close()

def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((proxy_host, proxy_port))
    server.listen(5)
    logger.info(f"Proxy server listening on {proxy_host}:{proxy_port}")

    while True:
        try:
            client_socket, addr = server.accept()
            logger.info(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        except Exception as e:
            logger.error(f"Error accepting connections: {e}")
    
if __name__ == "__main__":
    logger.info("Starting proxy")
    start_proxy()
import socket
import threading
import time


BUFFERSIZE = 10240
PORT = 8080
# HOST = socket.gethostbyname(socket.gethostname())
HOST = ""
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!quit"
content_type_dict = {
    "html": "text/html",
    "htm": "text/html",
    "txt": "text/plain",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "png": "image/png",
    "css": "text/css",
    "ico": "image/x-icon"
}


def read_request(client_socket):
    request = ""  # set this for time out case
    client_socket.settimeout(5)  # block socket operations for 5 sec

    try:
        request = client_socket.recv(BUFFERSIZE).decode()
    except TimeoutError:
        if not request:
            print("DIDN'T RECEIVE DATA. [TIMEOUT]")
    finally:
        return request


def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")

    while True:
        request = read_request(client_socket)
        if not request:
            # header = """HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"""
            header = """HTTP/1.1 200 OK\r\nConnection: close"""
            client_socket.send(header.encode())
            break

        if "POST" in request:
            if not check_login(request, client_socket):
                # client_socket.close()
                break
        print(f"[HTTP REQUEST]\n{request}")

        headers = request.split('\n')
        filename = headers[0].split()[1]
        if filename == '/':
            filename = 'index.html'

        if '.' in filename:
            file_type = filename.split('.')[1]
        else:
            file_type = ""
        # Return 404 when file does not exist
        try:
            with open('.' + filename, 'rb') as f:
                content = f.read()
        except FileNotFoundError:
            response = "HTTP/1.1 404 NOT FOUND\r\nConnection: close\r\n\r\nFile Not Found"
            client_socket.sendall(response.encode())
            break

        if file_type not in content_type_dict:
            content_type = "application/octet-stream"
        else:
            content_type = content_type_dict[file_type]

        # Send HTTP response
        header = """HTTP/1.1 200 OK\r\nConnection: keep-alive\r\nContent-Type: %s\r\nContent-Length: %s\r\n\r\n""" % (content_type, len(content))

        client_socket.send(header.encode())
        client_socket.send(content)

    client_socket.close()


def accept_incoming_connections(server_socket):
    """Sets up handling for incoming clients."""
    while True:
        client_socket, client_address = server_socket.accept()
        request_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        # request_thread.daemon = True
        request_thread.start()
        # request_thread.join()

        print(f"[NEW CONNECTION] {client_address} closed.")

    # handle_client(client_socket)


def check_login(request, client_socket):
    if "uname=admin&psw=123456" not in request:
        response = """HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n<!DOCTYPE html>
        <h1>401 Unauthorized</h1><p>This is a private area.</p>"""
        client_socket.send(response.encode())
        return False
    return True


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)


def start(server_socket):
    print(f"[LISTENING] Server is listening")
    server_socket.listen(1)
    accept_incoming_connections(server_socket)


start(server_socket)


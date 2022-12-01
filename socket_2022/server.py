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
    request = "timeout"
    client_socket.settimeout(5)  # block socket operations for 5 sec

    try:
        request = client_socket.recv(BUFFERSIZE).decode()
        if request == 0:
            return 0

    except TimeoutError:
        if request == "timeout":
            print("DIDN'T RECEIVE DATA. [TIMEOUT]")
    finally:
        return request


def handle_client(client_socket):
    # while True:
    request = read_request(client_socket)
    if "POST" in request:
        if not check_login(request, client_socket):
            client_socket.close()
    print(f"[HTTP REQUEST]\n{request}")

    # if request != "timeout" and request != "":
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
        client_socket.close()
        # break

    if file_type not in content_type_dict:
        content_type = "application/octet-stream"
    else:
        content_type = content_type_dict[file_type]

    # Send HTTP response
    response = """HTTP/1.1 200 OK\r
                        Content-Length: %s\r
                        Content-Type: %s\r\n\r\n""" % (len(content), content_type)

    client_socket.send(response.encode())
    client_socket.send(content)
    # else:
        # response = "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"""
        # client_socket.send(response.encode())
    client_socket.close()
        # break



def accept_incoming_connections(server_socket):
    """Sets up handling for incoming clients."""
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[NEW CONNECTION] {client_address} connected.")

        request_thread = threading.Thread(target=handle_client, args=(client_socket,))
        request_thread.daemon = True
        request_thread.start()
        request_thread.join()

        print(f"[NEW CONNECTION] {client_address} closed.")

    # handle_client(client_socket)


def check_login(request, client_socket):
    if "uname=admin&psw=123456" not in request:
        response = """HTTP/1.1 401 Unauthorized\r
                                   Connection: close\r\n\r
                                   <!DOCTYPE html>
               <h1>401 Unauthorized</h1><p>This is a private area.</p>"""
        client_socket.send(response.encode())
        return False
    return True


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)


def start():
    global server_socket
    print(f"[LISTENING] Server is listening")
    server_socket.listen(1)
    # accept_thread = threading.Thread(target=accept_incoming_connections, args=(server_socket,))
    # accept_thread.daemon = True
    # accept_thread.start()
    accept_incoming_connections(server_socket)


start()

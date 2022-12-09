import socket
import threading
import server_config
import os


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

    try:
        req = client_socket.recv(server_config.BUFFERSIZE).decode()
        while req:
            request += req
            req = client_socket.recv(server_config.BUFFERSIZE).decode()
    except socket.timeout:
        print("[TIMEOUT]")
        if not request:
            print("[DIDN'T RECEIVE REQUEST]")
    return request


def get_filename_content_type(headers):
    filename = headers[0].split()[1]
    if filename == '/':
        filename = 'index.html'

    if '.' in filename:
        file_type = filename.split('.')[1]
    else:
        file_type = ""
    if file_type not in content_type_dict:
        content_type = "application/octet-stream"
    else:
        content_type = content_type_dict[file_type]
    return filename, content_type


def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")

    while True:
        # request = read_request(client_socket)
        request = ""
        try:
            request = client_socket.recv(server_config.BUFFERSIZE).decode()
        except socket.timeout:
            print("[TIMEOUT]")

        if not request:
            header = """HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"""
            client_socket.send(header.encode())
            break

        if "POST" in request:
            if not check_login(request, client_socket):
                # client_socket.close()
                break

        headers = request.split('\n')
        print(f"[HTTP REQUEST]\n{headers[0]}")

        filename, content_type = get_filename_content_type(headers)
        # Return 404 when file does not exist
        try:
            f = open('.' + filename, 'rb')
            f.seek(0, os.SEEK_END)
            total = f.tell()
            f.seek(0)  # go back to the start
            data = f.read(server_config.BUFFERSIZE)
            header = """HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %s\r\n\r\n""" % (content_type, total)
            client_socket.sendall(header.encode())

            client_socket.send(data)
            while data:
                data = f.read(server_config.BUFFERSIZE)
                client_socket.send(data)

            f.close()
        except FileNotFoundError:
            response = "HTTP/1.1 404 NOT FOUND\r\nConnection: close\r\n\r\nFile Not Found"
            client_socket.sendall(response.encode())
            break

    client_socket.close()
    print(f"[NEW CONNECTION] {client_address} closed.")


def accept_incoming_connections(server_socket):
    """Sets up handling for incoming clients."""

    # while True:
    #     client_socket, client_address = server_socket.accept()
    #     client_socket.settimeout(20)
    #     request_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    #     request_thread.start()

    # Non-concurrency code:
    client_socket, client_address = server_socket.accept()
    # request_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_socket.settimeout(5)  # block socket operations for 5 sec
    handle_client(client_socket, client_address)


def check_login(request, client_socket):
    if "uname=admin&psw=123456" not in request:
        response = """HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n<!DOCTYPE html>
        <h1>401 Unauthorized</h1><p>This is a private area.</p>"""
        client_socket.send(response.encode())
        return False
    return True


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_config.ADDR)


def start(server_socket):
    print(f"[LISTENING] Server is listening")
    server_socket.listen(5)
    accept_incoming_connections(server_socket)


start(server_socket)


import socket
import threading
import server_config


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


def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")

    while True:
        # request = read_request(client_socket)
        client_socket.settimeout(5)
        try:
            request = client_socket.recv(server_config.BUFFERSIZE).decode()
        except socket.timeout:
            print("DIDN'T RECEIVE DATA. [TIMEOUT]")
            break

        if not request:
            # header = """HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"""
            header = """HTTP/1.1 200 OK\r\nConnection: close"""
            client_socket.send(header.encode())
            break

        if "POST" in request:
            if not check_login(request, client_socket):
                # client_socket.close()
                break

        headers = request.split('\n')
        print(f"[HTTP REQUEST]\n{headers[0]}")

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
        header = """HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %s\r\n\r\n""" % (content_type, len(content))

        client_socket.sendall(header.encode() + content)
        # client_socket.send(content)

    client_socket.close()
    print(f"[NEW CONNECTION] {client_address} closed.")


def accept_incoming_connections(server_socket):
    """Sets up handling for incoming clients."""
    while True:
        client_socket, client_address = server_socket.accept()
        request_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        # request_thread.daemon = True
        request_thread.start()
        request_thread.join()

        print(f"[NEW CONNECTION] {client_address} closed.")

    # # Non-concurrency code:
    # client_socket, client_address = server_socket.accept()
    # # request_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    # handle_client(client_socket, client_address)
    # print(f"[NEW CONNECTION] {client_address} closed.")

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


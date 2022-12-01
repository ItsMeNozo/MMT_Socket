import socket

# import threading

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
    "css": "text/css"
}


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# anything that connects to this ADDR (address) will hit this socket
# bind this socket to this address
server_socket.bind(ADDR)


def read_request(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    request = ""
    client_socket.settimeout(1)  # block socket operations for 1 sec
    try: 
        chunk = client_socket.recv(BUFFERSIZE).decode()
        request += chunk
        # keep reading if TCP request length > buffsize
        while chunk:
            chunk = client_socket.recv(BUFFERSIZE).decode()
            request += chunk
    except client_socket.timeout: 
        if request == "": 
            print("DIDN'T RECEIVE DATA. [TIMEOUT]")
    finally: 
        return request


def start():
    global server_socket
    print(f"[LISTENING] Server is listening")
    server_socket.listen(5)
    while True:
        client_socket, client_address = server_socket.accept()
        # thread = threading.Thread(target=read_request, args=(client_socket, client_address, request))
        # thread.start()
        request = read_request(client_socket, client_address)
        # print(f"[HTTP REQUEST]\n{request}")
        headers = request.split('\n')
        # print(f"Headers: {headers}")
        filename = headers[0].split()[1]
        if filename == '/':
            filename = '/index.html'
        file_type = filename.split('.')[1]

        with open('.' + filename, 'rb') as f:
            content = f.read()

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

        client_socket.close()  # temporarily put this here


start()

import socket 
# import threading
import time

BUFSIZE = 1024
PORT = 8080
# HOST = socket.gethostbyname(socket.gethostname())
HOST = ""
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!quit"

# create server socket
# client connect server -> read http request
# send http response
# close server
def create_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR) # bind this socket to this address so anything that connects to this ADDR (address) will hit this socket
    server_socket.listen(5) # question
    return server_socket


def read_request(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    request = ""
    client_socket.settimeout(1) # block socket operations for 1 sec
    try: 
        request = client_socket.recv(BUFSIZE).decode()
        # keep reading if TCP request length > buffsize
        while (request): 
            request += client_socket.recv(BUFSIZE).decode()
    except client_socket.timeout: 
        if request == "": 
            print("DIDN'T RECEIVE DATA. [TIMEOUT]")
    finally: 
        return request


def start(server_socket): 
    print(f"[LISTENING] Server is listening on {HOST}")
    request = ""
    while request == "": 
        client_socket, client_address = server_socket.accept()
        # thread = threading.Thread(target=read_request, args=(client_socket, client_address, request))
        # thread.start()
        request = read_request(client_socket, client_address)
        return client_socket, request


def send_file_index(client_socket): 
    with open("index.html", mode="rb") as index_file:# rb mode for non-text files
        contents = index_file.read()
    response_message = """HTTP/1.1 200 OK
    Content-Length: %d

    """%len(contents)
    print(f"[HTTP Response Message Index.html]\n{response_message}")
    response_message += contents.decode() # add body lines
    client_socket.send(bytes(response_message, 'utf-8'))


def load_page_index(server_socket, client_socket, request):
    if "GET /index.html HTTP/1.1" in request or "GET / HTTP/1.1" in request:
        send_file_index(client_socket)
        server_socket.close()
        return True

    
server_socket = create_server()
client_socket, request = start(server_socket)
print("[HTTP REQUEST]")
print(request)
load_page_index(server_socket, client_socket, request)
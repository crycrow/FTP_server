import socket

HOST = 'localhost'
PORT = 8080

while True:
    request = input('>')

    sock = socket.socket()
    sock.connect((HOST, PORT))

    sock.send(request.encode())
    if request == 'exit':
        sock.close()
        break

    response = sock.recv(1024).decode()
    print(response)

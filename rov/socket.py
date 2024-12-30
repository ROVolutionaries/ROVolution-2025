import socket

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to an address and port
server_socket.bind(('0.0.0.0', 5000))
# Enable the server to accept connections
server_socket.listen()
# Accept connection from client
client_socket, addr = server_socket.accept()
print(f"Got connection from {addr}")


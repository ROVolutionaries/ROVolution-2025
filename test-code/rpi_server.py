import socket
import time

bufferSize = 1024
msgFromServer = "Hello Client, Happy to be Your Server"
serverPort = 2222
serverIP = '192.168.68.100'
bytesToSend = msgFromServer.encode('utf-8')

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to an address and port
server_socket.bind((serverIP, serverPort))
print('Server is up and listening...')

message, address = server_socket.recvfrom(bufferSize)
message = message.decode('utf-8')
print("Message: ", message)
print("Client Address: ", address[0])

server_socket.sendto(bytesToSend, address)




'''
# Enable the server to accept connections
server_socket.listen()
# Accept connection from client
client_socket, addr = server_socket.accept()
print(f"Got connection from {addr}")
'''

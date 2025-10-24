import socket
import serial
import time

msgFromClient = 'Hello'
bytesToSend = msgFromClient.encode('utf-8')
serverAddress = ('169.254.37.82', 2222)
bufferSize = 1024

UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPClient.sendto(bytesToSend,serverAddress)

data, address = UDPClient.recvfrom(bufferSize)
data = data.decode('utf-8')
print("Data from Server: ", data)
print("Server IP Address: ", address)
print("Server Port: ", address[1])
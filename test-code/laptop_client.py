import socket
import serial
import time

ser = serial.Serial('/dev/serial0', 115200, timeout=5)

msgFromClient = 'Hello Server, from Your Client'
bytesToSend = msgFromClient.encode('utf-8')
serverAddress = ('192.168.68.115', 2222)
bufferSize = 1024

UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPClient.sendto(bytesToSend,serverAddress)

data, address = UDPClient.recvfrom(bufferSize)
data = data.decode('utf-8')
print("Data from Server: ", data)
print("Server IP Address: ", address)
print("Server Port: ", address[1])
import socket
import sys
import time
import os
import psutil

def get_cpu():
    cpu_usage = psutil.cpu_percent(interval=1)
    message_float = cpu_usage
    message = str(message_float)
    print("CPU ", message_float)
    return str(message_float)

def get_vmemory():
    vm = psutil.virtual_memory()
    total = vm.percent

    message_float = str(total)
    print("Virtual Memory ", message_float)
    return str(message_float)

HOST, PORT = "localhost", 8888

while True:
    data = "Client 2"
    data2 = get_vmemory()
    time.sleep(10)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.sendto(data + "\n", (HOST, PORT))
    sock.sendto(data2 + "\n", (HOST, PORT))
    received = sock.recv(1024)



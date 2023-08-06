import socket
import random
from threading import Thread
from datetime import datetime
import os

# server's IP address
# if the server is not on this machine, 
# put the private (network) IP address (e.g 192.168.1.2)
SERVER_HOST = "192.168.1.6"
SERVER_PORT = 8080 # server's port
separator_token = "<SEP>" # we will use this to separate the client name & message
excode = False

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")
# prompt the client for a name
name = input("Enter your name: ")

def listen_for_messages():
	while True:
		message = s.recv(1024).decode()
		if message == "server!exit!code":
			excode = True
		else:
			print("\n" + message)

def file_transfer(file_name):
	try:
		file = open(file_name, "rb")
	except Exception as e:
		print("Cannot open file.\n" + "-"*20 + f"\n{e}\n" + "-"*20  + "\n")
		return 0

	s.send("file!transfer!code".encode())
	file_size = os.path.getsize(file_name)
	rem = int(file_size % 4096)
	quo = int((file_size - rem)/4096)
	packet_info = str(quo) + ":@!$" + str(rem) + ":@!$" + file_name + ":@!$" + name + ":@!$"
	send_packet = packet_info.ljust(256, "#")
	s.send(send_packet.encode())

	# packet transmission
	s.sendall(file.read())

	file.close()
	return 0

def file_download(file_name):
	s.send("file!download!request".encode())
	needed = file_name + ":@!"
	needed_packet = needed.ljust(256, "#")
	s.send(needed_packet.encode())
	packet_info = s.recv(256).decode()
	packet_struct = packet_info.split(":@!")
	
	rem = int(packet_struct[1])
	quo = int(packet_struct[0])
	print(rem, ", ", quo)

	file = open(packet_struct[2], "wb")
	data = bytearray()
	count = 0
	packet = 0
	while count <= quo + 1:
		packet = cs.recv(4096)
		data += packet
		count += 1
	
	file.write(data)
	file.close()
	print("file downloaded... ", f"file name: {packet_struct[2]}, size: {packet_struct[0]*4096 + packet_struct[1]} bytes.\n")

# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

while True:
	# input message we want to send to the server
	date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	to_send =  input()
	# a way to exit the program
	if to_send.lower() == 'quit' or excode:
		quit_code = "client!exit!code"
		s.send(quit_code.encode())
		break

	elif to_send.strip() == "!upload file":
		fileName = input("Enter file name: ")
		f_t = Thread(target = file_transfer, args = (fileName,))
		f_t.daemon = True
		f_t.start()

	elif to_send.strip() == "!download file":
		fileName = input("Enter <user>__<file name>: ")
		f_d = Thread(target = file_download, args = (fileName,))
		f_d.daemon = True
		f_d.start()

	else:
		# add the datetime, name & the color of the sender
		to_send = f"[{date_now}] {name}{separator_token}{to_send}"
		# finally, send the message
		s.send(to_send.encode())

# close the socket
s.close()

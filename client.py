'''

	Written by Azorfus
	Github: @azorfus

'''

import socket
import threading
import time
from datetime import datetime
import os

SERVER_HOST = "192.168.1.11"
SERVER_PORT = 8080
separator_token = "<SEP>"

fsport = 0

s = socket.socket()

# event = threading.Event()
# event.set()

try:
	s.connect((SERVER_HOST, SERVER_PORT))
	fsport = int(s.recv(256).decode().split("!@$:")[0])
	print("File transport port: ", fsport)

except ConnectionRefusedError:
	print("Server is not available. Exiting...")
	exit(1)

print(f"[*] Connected to {SERVER_HOST}:{SERVER_PORT}.")

name = input("Enter your name: ")

def listen_for_messages():
	while True:
		#if event.is_set():
		msg_R = s.recv(1024).decode('utf-8', errors='ignore')
		msg = msg_R.split("!@$:")[0]
		if msg == "server!abort!code!abort":
			s.close()
			break
		if msg != "file!download!incoming":
			print("\n" + msg)
		#else:
		#	print("Paused Thread")
		#	event.wait()
		

def file_transfer(file_name):
	try:
		file = open(file_name, "rb")
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

	except Exception as e:
		print(f"[!] Error: {e}")
		return 0

	return 0

def file_download(file_name):
	print("\n[*] Establishing tunnel to server, this may take a moment...")
	time.sleep(2)
	fs = socket.socket()
	try:
		fs.connect((SERVER_HOST, fsport))
		print(f"[*] Established tunnel to server on port: {fsport}")
		packet_info_R = fs.recv(256)
		packet_info = packet_info_R.decode('utf-8', errors='ignore')
		packet_struct = packet_info.split(":@!")
	
		rem = int(packet_struct[1])
		quo = int(packet_struct[0])
		req_file = packet_struct[2]
	
		with open(req_file, "wb") as f:
	
			data = bytearray()
			count = 0
			packet = 0
			while count <= quo:
				if count == quo:
					packet = fs.recv(rem)
				else:
					packet = fs.recv(4096)
		
				data += packet
				count += 1
		
			f.write(data)
			f.close()
		print("[*] Closing file transfer tunnel...")
		fs.close()
		print("File downloaded...", f"file name: {packet_struct[2]}, size: {quo * 4096 + rem} bytes.\n")

	except Exception as e:
		print(f"[!] Could not establish file transfer tunnel.\nError: {e}")
		fs.close()
		return 0
	return 0

lisn = threading.Thread(target = listen_for_messages)
lisn.daemon = True
lisn.start()

while True:
	date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	to_send = input()

	try:
		if to_send.lower() == 'quit':
			to_send = "client!exit!code!@:"
			s.send(to_send.ljust(1024, "#").encode())
			break
	
		elif to_send.strip() == "!upload file":
			fileName = input("Enter file name: ")
			file_transfer(fileName)
	
		elif to_send.strip() == "!download file":
			fileName = input("Enter <user>__<file name>: ")
			to_send = "file!download!request!@$:" + fileName + "!@:"
			s.send(to_send.ljust(1024, "#").encode())
			file_download(fileName)
	
		else:
			to_send = f"[{date_now}] {name}{separator_token}{to_send}!@:"
			s.send(to_send.ljust(1024, "#").encode())
		
	except Exception as e:
		print(f"[!] Error: {e}")

s.close()



'''

	Written by Azorfus
	Github: @azorfus

'''

import socket
import threading
import time
import os

host = str(input("Enter Host IP: "))
port = 8080
sep_tok = "<SEP>"
MAX_LISTEN_TIME = 2
exit_flag = threading.Event()

client_sockets = []
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(20)

print(f"[*] Listening as {host}:{port}")

def send_file(cs, file_name):
	try:
		file = open(file_name, "rb")
		file_size = os.path.getsize(file_name)

		rem = int(file_size % 4096)
		quo = int((file_size - rem)/4096)
		file_name_back = file_name.split("__")[1]
	
		# Packet with file size and name information.
		packet_info = str(quo) + ":@!" + str(rem) + ":@!" + file_name_back + ":@!"
		send_packet = packet_info.ljust(256, "#")
		cs.send(send_packet.encode())
		cs.sendall(file.read())
		
		file.close()

	except Exception as e:
		print(f"[!] Error: {e}")
		return 0

	return 0
	


def establish_conn(cs, file_name):

	# Start time of the server
	start_time = time.time()

	fs = socket.socket()
	fs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	fs.bind((host, fport))
	print("[*] Listening for file tunnel connection...")

	# Listen for file tunnel connections within the time limit
	fs.listen(1)
	while (time.time() - start_time) <= MAX_LISTEN_TIME:
		try:
			fcs, fcaddr = fs.accept()
			print(f"[*] File transfer tunnel established with {fcaddr}")
			send_file(fcs, file_name)
			print(f"[*] File transfer tunnel successfully closing...")
		except socket.timeout:
			print("Timing out...")
			pass  # Ignore timeout and continue listening

	fs.close()


def recv_file(cs):
	cs_ip = cs.getpeername()

	packet_info = cs.recv(256).decode('utf-8', errors='ignore')
	packet_struct = packet_info.split(":@!$")

	rem = int(packet_struct[1])
	quo = int(packet_struct[0])

	with open(f"{packet_struct[3]}__{packet_struct[2]}", "wb") as file:

		count = 0
		packet = 0
		while count <= quo:
			if count == quo:
				packet = cs.recv(rem)
			else:
				packet = cs.recv(4096)
			file.write(packet)
			count += 1

		file.close()

	upload_info = f"{packet_struct[3]} uploaded file {packet_struct[2]} size: {quo*4096+rem} bytes.\nTo download the file, Type \"!download file\" and then enter the file name in the format <username>__<file name>i.e. \"{packet_struct[3]}__{packet_struct[2]}\"\n"
	for client_socket in client_sockets:
		client_socket.send(upload_info.encode())
	return 0

def establish_conn_recv(cs):

	# Start time of the server
	start_time = time.time()

	fs = socket.socket()
	fs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	fs.bind((host, fport))
	print("[*] Listening for file tunnel connection...")

	# Listen for file tunnel connections within the time limit
	fs.listen(1)
	while (time.time() - start_time) <= MAX_LISTEN_TIME:
		try:
			fcs, fcaddr = fs.accept()
			print(f"[*] File transfer tunnel established with {fcaddr}")
			recv_file(fcs)
			print(f"[*] File transfer tunnel successfully closing...")
		except socket.timeout:
			print("Timing out...")
			pass  # Ignore timeout and continue listening

	fs.close()

def listen_for_client(cs):
	while not exit_flag.is_set():
		try:
			msg_R = cs.recv(1024).decode('utf-8', errors='ignore')
			msg = msg_R.split("!@:")[0]

			if msg == "client!exit!code":
				print(f"[*] Client: {cs.getpeername()[0]} has closed the connection.")
				client_sockets.remove(cs)
				cs.close()
				break

			elif msg == "file!transfer!code":
				establish_conn_recv(cs)

			elif msg.split("!@$:")[0] == "file!download!request":
				file_name = msg.split("!@$:")[1]
				establish_conn(cs, file_name)

			else:
				msg_R = msg.replace(sep_tok, ": ") + "!@$:"
				msg = msg_R.ljust(1024, "#")
				for client_socket in client_sockets:
					client_socket.send(msg.encode())

		except Exception as e:
			print(f"[!] Error: {e}")
			client_sockets.remove(cs)
			cs.close()
			break

def server_term():
	while not exit_flag.is_set():
		cmd = input("$ ")
		if cmd == "ABORT":
			exit_flag.set()
			for i in threading.enumerate():
				i.join()
			for cs in client_sockets:
				abort_code = "server!abort!code!abort!@$:".ljust(1024, "#")
				cs.send(abort_code.encode())
				cs.close()
			s.close()
			break 


term = threading.Thread(target = server_term)
term.daemon = True
term.start()

while True:
	client_socket, client_address = s.accept()
	print(f"[+] {client_address} connected.")
	client_sockets.append(client_socket)

	fport = 8081 + client_sockets.index(client_socket)
	sport = f"{fport}!@$:".ljust(256, "#")
	client_socket.send(sport.encode())

	client_t = threading.Thread(target=listen_for_client, args=(client_socket,))
	client_t.daemon = True
	client_t.start()

s.close()

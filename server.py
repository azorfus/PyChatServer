import socket
from threading import Thread
import os

host = "192.168.1.6"
port = 8080
sep_tok = "<SEP>"

client_sockets = set()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(10)

running = True

print(f"[*] Listening as {host}:{port}")

def send_file(cs):
	file_name_raw = cs.recv(256).decode()
	file_name = file_name_raw.split(":@!")[0]

	try:
		file = open(file_name, "rb")
	except Exception as e:
		print("Cannot open file.\n" + "-"*20 + f"\n{e}\n" + "-"*20  + "\n")
		return 0

	file_size = os.path.getsize(file_name)

	rem = int(file_size % 4096)
	quo = int((file_size - rem)/4096)
	file_name_back = file_name.split("__")[1]

	packet_info = str(quo) + ":@!$" + str(rem) + ":@!$" + file_name_back + ":@!$"
	send_packet = packet_info.ljust(256, "#")
	s.send(send_packet.encode())
	s.sendall(file.read())
	file.close()
	return 0
	

def recv_file(cs):
	cs_ip = cs.getpeername()

	packet_info = cs.recv(256).decode()
	packet_struct = packet_info.split(":@!$")

	rem = int(packet_struct[1])
	quo = int(packet_struct[0])
	print(rem, ", ", quo)

	file = open(f"{packet_struct[3]}__{packet_struct[2]}", "wb")

	data = bytearray()
	count = 0
	packet = 0
	while count <= quo+1:
		packet = cs.recv(4096)
		data += packet
		count += 1

	file.write(data)
	file.close()
	upload_info = f"{packet_struct[3]} uploaded file {packet_struct[2]} size: {quo*4096+rem} bytes.\nTo download the file, Type \"!download file\" and then enter the file name in the format <username>__<file name>i.e. \"{packet_struct[3]}__{packet_struct[2]}\"\n"
	for client_socket in client_sockets:
		client_socket.send(upload_info.encode())
	return 0

def listen_for_client(cs):
	dont = False
	while True:
		try:
			msg = cs.recv(1024).decode()
			if msg == "client!exit!code":
				client_sockets.remove(cs)
			elif msg == "file!transfer!code":
				recv_file(cs)
			elif msg == "file!download!request":
				send_file(cs)

		except Exception as e:
			print(f"[!] Error: {e}")
			client_sockets.remove(cs)
		else:
			if not dont:
				msg = msg.replace(sep_tok, ": ")
				for client_socket in client_sockets:
					client_socket.send(msg.encode())

"""
def server_term():
	while True:
		cmd = input("$> ")
		if cmd == "quit":
			running = False
			for cs in client_sockets:
				cs.close()
			s.close()
			# close server socket
"""
while running:

	# we keep listening for new connections all the time
	client_socket, client_address = s.accept()
	print(f"[+] {client_address} connected.")
	# add the new connected client to connected sockets
	client_sockets.add(client_socket)
	# start a new thread that listens for each client's messages

#	cmd = Thread(target = server_term, args = ())
	t = Thread(target=listen_for_client, args=(client_socket,))
#	cmd.daemon = True

	# make the thread daemon so it ends whenever the main thread ends
	t.daemon = True
	# start the thread
#	cmd.start()
	t.start()

# close client sockets
for cs in client_sockets:
	cs.close()
	# close server socket
s.close()

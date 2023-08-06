import socket
from threading import Thread

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

def recv_file(cs):
	cs_ip = cs.getpeername()

	packet_info = cs.recv(256).decode()
	packet_struct = packet_info.split(":@!$")

	rem = int(packet_struct[1])
	quo = int(packet_struct[0])

	file = open(f"{packet_struct[3]}__{packet_struct[2]}", "wb")

	data = bytearray()
	count = 0
	packet = 0
	while count <= quo:
		packet = cs.recv(4096)
		data += packet
		count += 1
	'''
		if count == quo:
			packet = cs.recv(4096)
			data += packet
			print("[*] Last packet data:\n", packet)
		else:
			packet = cs.recv(4096)
			data += packet
	'''

	file.write(data)
	file.close()
	upload_info = f"{packet_struct[3]} uploaded file {packet_struct[2]} size: {quo*4096+rem} bytes.\nTo download the file, Type \"!download file\" and then enter the file name in the format <username>__<file name>i.e. \"{packet_struct[3]}__{packet_struct[2]}\""
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
				f_recv = Thread(target = recv_file, args = (cs,))
				f_recv.daemon = True
				f_recv.start()
				dont = True
			else:
				dont = False
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

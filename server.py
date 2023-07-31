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

def listen_for_client(cs):
	while True:
		try:
			msg = cs.recv(1024).decode()
		except Exception as e:
			print(f"[!] Error: {e}")
			client_sockets.remove(cs)
		else:
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

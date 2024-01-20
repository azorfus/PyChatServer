import socket
import threading
import time
from datetime import datetime
import os

SERVER_HOST = str(input("Enter Host IP: "))
SERVER_PORT = 8080

s = socket.socket()

try:
	s.connect((SERVER_HOST, SERVER_PORT))

except ConnectionRefusedError:
	print("Server is not available. Exiting...")
	exit(1)

print(f"[*] Connected to {SERVER_HOST}:{SERVER_PORT}.")

name = input("Enter your name: ")
date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
to_send = f"{name} has connected."
conn_init = f"{date_now}!@$#:server!@$#:{to_send}!@$:"
s.send(conn_init.ljust(1024, "#").encode())

def listen_for_messages():
	while True:
		#if event.is_set():
		msg_R = s.recv(1024).decode('utf-8', errors='ignore')
		msg = msg_R.split("!@$:")[0]

		if msg == "server!abort!code!abort":
			s.close()
			break
		else:
			print(msg)

lisn = threading.Thread(target = listen_for_messages)
lisn.daemon = True
lisn.start()

while True:

	date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	to_send = input()

	if len(to_send) >= 1024:
		print("\n[!] Message size limit is 1024 characters. Please send a message within the size limit.\n")

	else:

		try:

			if to_send.lower() == 'quit':
				to_send = "client!exit!code!@$:"
				s.send(to_send.ljust(1024, "#").encode())
				break

			else:
				to_send = f"{date_now}!@$#:{name}!@$#:{to_send}!@$:"
				s.send(to_send.ljust(1024, "#").encode())
			
		except Exception as e:
			print(f"[!] Error: {e}")
			if "Errno 9" in str(e):
				print("[!] Server has aborted!!! Exiting...")
				break

s.close()


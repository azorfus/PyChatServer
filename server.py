import socket
import threading
import os
import sys
import csv

host = str(input("Enter Host IP: "))
port = 8080
MAX_LISTEN_TIME = 2
exit_flag = threading.Event()
exit_flag.set()
msg_count = 0

client_sockets = []
client_threads = {}
ban_list = []
s = socket.socket()

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))

s.listen(20)

print(f"[*] Listening as {host}:{port}")

def listen_for_client(cs):

	global logfile
	global log_writer
	global msg_count
	global client_sockets
	global client_threads
	while exit_flag.is_set() and client_threads[cs][1].is_set():

		if not client_threads[cs][1].is_set():
			break

		try:	
			msg_R = cs.recv(1024).decode('utf-8', errors='ignore')
			msg = msg_R.split("!@$:")[0]
			msg_count = msg_count + 1

			if msg_count >= 20:
				logfile.flush()
				msg_count = 0

			if msg == "client!exit!code":
				print(f"[*] Client: {cs.getpeername()[0]} has closed the connection.")
				log_writer.writerow([" ", " ", "Closing Connection", cs.getpeername()[0]])
				client_sockets.remove(cs)
				cs.close()
				break

			else:
				if client_threads[cs][1].is_set():
					info = msg_R.split("!@$#:")
					log_writer.writerow([info[0], info[1], info[2].split("!@$:")[0], cs.getpeername()[0]])
					msg_R = f"[{info[0]}] {info[1]}: {info[2]}!@$:"
					msg = msg_R.ljust(1024, "#")
					for client_socket in client_sockets:
						client_socket.send(msg.encode())

		except Exception as e:
			if client_threads[cs][1].is_set():
				print(f"[!] Error: {e}, A client probably aburptly ended the session.")
				client_sockets.remove(cs)
				client_threads[cs][1].clear()
				cs.close()
				return


def server_term():

	global logfile
	global exit_flag
	global client_sockets

	while exit_flag.is_set():

		cmd = input("$ ")
		if cmd == "abort":

			exit_flag.clear()

			clients_to_remove = []

			for cs in client_sockets:
				abort_code = "server!abort!code!abort!@$:".ljust(1024, "#")
				cs.send(abort_code.encode())
				clients_to_remove.append(cs)

			for cs in clients_to_remove:
				client_sockets.remove(cs)
				cs.close()

			os._exit(0)

		elif cmd == "logflush":
			# flushing all logging data to csv file from buffer.
			logfile.flush()

		elif cmd == "kick":
			found = False
			user_ip_to_kick = str(input("Enter IP of user to be kicked: "))
			for cs in client_sockets:
				if cs.getpeername()[0] == user_ip_to_kick:
					client_sockets.remove(cs)
					client_threads[cs][1].clear()
					cs.close()
					print(f"[!] User: {user_ip_to_kick} has been kicked!")
					found = true

			if not found:
				print("[!] Given IP is not connected!")

		elif cmd == "ban":
			found = False
			user_ip_to_ban = str(input("Enter IP of user to be banned: "))
			for cs in client_sockets:
				if cs.getpeername()[0] == user_ip_to_ban:
					client_sockets.remove(cs)
					client_threads[cs][1].clear()
					cs.close()
					ban_list.append(user_ip_to_ban)
					print(f"[!] User: {user_ip_to_ban} has been banned!")
					found = True

			if not found:
				print("[!] Given IP is not connected!")

		elif cmd == "unban":
			user_ip_to_unban = str(input("Enter IP of user to be unbanned: "))
			if user_ip_to_unban in ban_list:
				ban_list.remove(user_ip_to_unban)
				print("[!] User has been unbanned!")
			else:
				print("[!] Given IP is not banned!")

		elif cmd == "connections":
			for cs in client_sockets:
				print("[Connected User] ", cs.getpeername()[0])

		elif cmd == "banlist":
			for cs in ban_list:
				print("[Banned User] ", cs)



with open("logfile.csv", "a+") as logfile:

	log_writer = csv.writer(logfile, delimiter=",")

	term = threading.Thread(target = server_term)
	
	term.daemon = True
	term.start()
	
	while True:
		if not exit_flag.is_set:
			break

		client_socket, client_address = s.accept()

		if client_socket.getpeername()[0] in ban_list:
			client_socket.close()

		else:
			print(f"[+] {client_address} connected.")
			client_sockets.append(client_socket)
		
			client_t = threading.Thread(target=listen_for_client, args=(client_socket,))
			client_t.daemon = True
			u_flag = threading.Event()
			u_flag.set()

			client_threads[client_socket] = [client_t, u_flag]
			client_threads[client_socket][0].start()

s.close()
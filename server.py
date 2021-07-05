import socket
from _thread import *
import pickle
import time
import random
import math

sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

PORT = 5555

BALL_RADIUS = 5
START_RADIUS = 7

#MAXIMAL WAKTU 5 MENIT
ROUND_TIME = 60 * 5

#INTERVAL WAKTU BOLA AGAR MENGECIL
MASS_LOSS_TIME = 7

W, H = 1200, 720


# TRY TO CONNECT TO SERVER
try:
    sock_server.bind((SERVER_IP, PORT))

except socket.error as e:
    print(str(e))
    print("[SERVER] Server could not start")
    quit()

sock_server.listen(5)
print(f"[SERVER] Server Started with local ip {SERVER_IP}")

clients = {}
balls = []
connections = 0
_id = 0
colors = [(255,0,0), (255, 128, 0), (255,255,0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (0,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (0,0,0)]
start = False
stat_time = 0
game_time = "Starting Soon"
nxt = 1


# FUNCTIONS

def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)

def send_msg(sock_cli, data):
    sock_cli.send(bytes(data, "utf-8"))

#FUNGSI UNTUK MENGATUR JELLO AGAR MENGECIL DENGAN INTERVAL
def release_mass(clients):
	for player in clients:
		p = clients[player]
		if p["score"] > 8:
			p["score"] = math.floor(p["score"]*0.95)

#FUNGSI UNTUK MENGECEK APAKAH ADA TABRAKAN ANTARA PLAYER DENGAN BOLA
def check_collision(clients, balls):
	to_delete = []
	for player in clients:
		p = clients[player]
		x = p["x"]
		y = p["y"]
		for ball in balls:
			bx = ball[0]
			by = ball[1]

			dis = math.sqrt((x - bx)**2 + (y-by)**2)
			if dis <= START_RADIUS + p["score"]:
				p["score"] = p["score"] + 0.5
				balls.remove(ball)

#FUNGSI UNTUK MENGECEK APAKAH ADA TABRAKAN ANTAR PLAYER
def player_collision(clients):
	sort_clients = sorted(clients, key=lambda x: clients[x]["score"])
	for x, player1 in enumerate(sort_clients):
		for player2 in sort_clients[x+1:]:
			p1x = clients[player1]["x"]
			p1y = clients[player1]["y"]

			p2x = clients[player2]["x"]
			p2y = clients[player2]["y"]

			dis = math.sqrt((p1x - p2x)**2 + (p1y-p2y)**2)
			if dis < clients[player2]["score"] - clients[player1]["score"]*0.85:
				clients[player2]["score"] = math.sqrt(clients[player2]["score"]**2 + clients[player1]["score"]**2) # adding areas instead of radii
				clients[player1]["score"] = 0
				clients[player1]["x"], clients[player1]["y"] = get_start_location(clients)
				print(f"[GAME] " + clients[player2]["name"] + " ATE " + clients[player1]["name"])

#FUNGSI UNTUK GENERATE BOLA-BOLA YANG BISA DIMAKAN OLEH JELLO DENGAN RANDOM
def create_balls(balls, n):
	for i in range(n):
		while True:
			stop = True
			x = random.randrange(0,W)
			y = random.randrange(0,H)
			for player in clients:
				p = clients[player]
				dis = math.sqrt((x - p["x"])**2 + (y-p["y"])**2)
				if dis <= START_RADIUS + p["score"]:
					stop = False
			if stop:
				break

		balls.append((x,y, random.choice(colors)))

#FUNGSI UNTUK MENENTUKAN LOKASI AWAL PLAYER DENGAN RANDOM
def get_start_location(clients):
	while True:
		stop = True
		x = random.randrange(0,W)
		y = random.randrange(0,H)
		for player in clients:
			p = clients[player]
			dis = math.sqrt((x - p["x"])**2 + (y-p["y"])**2)
			if dis <= START_RADIUS + p["score"]:
				stop = False
				break
		if stop:
			break
	return (x,y)

#FUNGSI UNTUK MEMBUAT THREAD UNTUK TIAP PLAYER DALAM SERVER
def threaded_client(conn, _id):
	global connections, clients, balls, game_time, nxt, start

	current_id = _id

	#MENERIMA NAMA DARI PLAYER
	username_client = conn.recv(16).decode("utf-8")
	print("[LOG]", username_client, "connected to the server.")

	#MEMBUAT PROPERTI UNTUK PLAYER
	color = colors[current_id]
	x, y = get_start_location(clients)
	clients[current_id] = {"x":x, "y":y,"color":color,"score":0,"name":username_client}  # x, y color, score, name

	# MENGIRIM DATA KE CLIENT
	conn.send(str.encode(str(current_id)))

	# server will recieve basic commands from client
	# it will send back all of the other clients info

	while True:

		if start:
			game_time = round(time.time()-start_time)
			#MENGHENTIKAN GAME APABILA SUDAH LEBIH 5 MENIT DARI WAKTU SERVER
			if game_time >= ROUND_TIME:
				start = False
			else:
				if game_time // MASS_LOSS_TIME == nxt:
					nxt += 1
					release_mass(clients)
					print(f"[GAME] {username_client}'s Mass depleting")
		try:
			# MENERIMA DATA DARI CLIENT
			data = conn.recv(1024)

			if not data:
				break

			data = data.decode("utf-8")
			#print("[DATA] Recieved", data, "from client id:", current_id)

			# MENCARI COMMAND MOVE & MENGUBAH LOKASI PLAYER
			if data.split(" ")[0] == "move":
				split_data = data.split(" ")
				x = int(split_data[1])
				y = int(split_data[2])
				clients[current_id]["x"] = x
				clients[current_id]["y"] = y

				# CHECK COLLISION
				if start:
					check_collision(clients, balls)
					player_collision(clients)

				# GENERATE BOLA MAKANAN APABILA KURANG DARI 150
				if len(balls) < 150:
					create_balls(balls, random.randrange(100,150))
					print("[GAME] Generating more orbs")

				send_data = pickle.dumps((balls,clients, game_time))

			elif data.split(" ")[0] == "id":
				send_data = str.encode(str(current_id)) 

			elif data.split(" ")[0] == "jump":
				send_data = pickle.dumps((balls,clients, game_time))
			else:
				# any other command just send back list of clients
				send_data = pickle.dumps((balls,clients, game_time))

			# SEND DATA KE CLIENTS
			conn.send(send_data)

		except Exception as e:
			print(e)
			break 

		time.sleep(0.001)

	# When user disconnects	
	print("[DISCONNECT] Name:", username_client, ", Client Id:", current_id, "disconnected")

	connections -= 1 
	del clients[current_id]  # REMOVE FROM PLAYER LIST
	conn.close()  # CLOSE CONNECTION


# MAINLOOP

# MEMBUAT BOLA-BOLA MAKANAN
create_balls(balls, random.randrange(200,250))

print("[GAME] Setting up level")
print("[SERVER] Waiting for connections")

# MENERIMA KONEKSI SELAMA SERVER HIDUP
while True:
	
	sock_client, addr_client = sock_server.accept()
	print("[CONNECTION] Connected to:", addr_client)

	#MEMULAI GAME APABILA ADA CLIENTS YANG TERKONEKSI
	if addr_client[0] == SERVER_IP and not(start):
		start = True
		start_time = time.time()
		print("[STARTED] Game Started")

	# MEMBUAT THREAD UNTUK CLIENT TERSEBUT
	connections += 1
	start_new_thread(threaded_client,(sock_client,_id))
	_id += 1

# END PROGRAM
print("[SERVER] Server offline")

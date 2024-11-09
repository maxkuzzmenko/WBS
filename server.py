import socket
import threading
import json

# Server Configuration
SERVER_IP = "0.0.0.0"  # Use "0.0.0.0" to listen on all network interfaces
SERVER_PORT = 5555
clients = {}
lock = threading.Lock()

# Function to handle individual client connections
def handle_client(conn, addr):
    player_id = addr[1]
    clients[player_id] = {"x": 100, "y": 500, "health": 100}  # Initial player state

    try:
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            # Decode and update the player's data
            player_data = json.loads(data)
            with lock:
                clients[player_id] = player_data

            # Broadcast the updated state to all clients
            broadcast_data = json.dumps(clients)
            for client_conn in list(clients.keys()):
                if client_conn != player_id:  # Avoid sending data to the sender
                    try:
                        conn.send(broadcast_data.encode("utf-8"))
                    except:
                        del clients[client_conn]
    except:
        pass
    finally:
        # Disconnect client
        with lock:
            del clients[player_id]
        conn.close()

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()
    print(f"[SERVER] Listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        threading.Thread(target=handle_client, args=(conn, addr)).start()

start_server()

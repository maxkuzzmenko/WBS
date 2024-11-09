import socket
import threading
import json

# Server Configuration
SERVER_IP = "0.0.0.0"  # Set to 0.0.0.0 to listen on all interfaces
SERVER_PORT = 5555
clients = {}
lock = threading.Lock()

# Handle each client connection
def handle_client(conn, addr):
    player_id = addr[1]  # Unique ID based on the client's port number
    clients[player_id] = {"x": 100, "y": 500, "health": 100, "color": "BLUE"}  # Initial player state

    try:
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            # Update player state with received data
            player_data = json.loads(data)
            with lock:
                clients[player_id] = player_data

            # Broadcast updated state to all clients
            broadcast_data = json.dumps(clients)
            for pid, client_conn in list(clients.items()):
                if pid != player_id:  # Avoid sending data back to the sender
                    try:
                        conn.send(broadcast_data.encode("utf-8"))
                    except:
                        del clients[pid]
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        # Remove the client upon disconnect
        with lock:
            del clients[player_id]
        conn.close()

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        conn, addr = server.accept()
        print(f"New connection: {addr}")
        threading.Thread(target=handle_client, args=(conn, addr)).start()

start_server()

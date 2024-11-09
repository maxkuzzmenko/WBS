import socket
import threading
import json

# Server configuration
SERVER_IP = "127.0.0.1"  # Replace with public IP for global access
SERVER_PORT = 5555
clients = {}
lock = threading.Lock()

# Handle incoming messages from clients
def handle_client(conn, addr):
    global clients
    print(f"[NEW CONNECTION] {addr} connected.")
    player_id = addr[1]
    clients[player_id] = {"x": 100, "y": 500, "health": 100}

    try:
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            player_data = json.loads(data)
            with lock:
                clients[player_id] = player_data

            # Broadcast updated player states to all clients
            broadcast_data = json.dumps(clients)
            for client_conn in list(clients.keys()):
                try:
                    conn.send(broadcast_data.encode("utf-8"))
                except:
                    del clients[client_conn]
    except Exception as e:
        print(f"[ERROR] {e}")

    # Handle disconnection
    print(f"[DISCONNECT] {addr} disconnected.")
    with lock:
        del clients[player_id]
    conn.close()

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()

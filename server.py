import socket
import threading
import json
import random

# Server Configuration
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5555
rooms = {}  # Format: { room_id: {"players": [conn1, conn2, ...], "max_players": 5} }
lock = threading.Lock()

# Handle each client connection
def handle_client(conn, addr):
    current_room_id = None
    try:
        while True:
            # Receive message from client
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            # Parse the message as JSON
            message = json.loads(data)
            action = message["action"]

            if action == "create_room":
                # Generate a unique room ID and create a new room
                room_id = str(random.randint(1000, 9999))
                with lock:
                    rooms[room_id] = {"players": [conn], "max_players": 5}
                current_room_id = room_id
                conn.send(json.dumps({"status": "room_created", "room_id": room_id}).encode("utf-8"))

            elif action == "join_room":
                room_id = message["room_id"]
                with lock:
                    if room_id in rooms and len(rooms[room_id]["players"]) < rooms[room_id]["max_players"]:
                        rooms[room_id]["players"].append(conn)
                        current_room_id = room_id
                        conn.send(json.dumps({"status": "joined_room", "room_id": room_id}).encode("utf-8"))
                        # Notify all players in the room of the new player
                        for player_conn in rooms[room_id]["players"]:
                            if player_conn != conn:
                                player_conn.send(json.dumps({"status": "player_joined"}).encode("utf-8"))
                    else:
                        conn.send(json.dumps({"status": "error", "message": "Room full or doesn't exist"}).encode("utf-8"))

            elif action == "leave_room":
                if current_room_id:
                    with lock:
                        rooms[current_room_id]["players"].remove(conn)
                        if not rooms[current_room_id]["players"]:
                            del rooms[current_room_id]
                        else:
                            for player_conn in rooms[current_room_id]["players"]:
                                player_conn.send(json.dumps({"status": "player_left"}).encode("utf-8"))
                    current_room_id = None

            elif action == "send_message":
                # Broadcast message to all players in the current room
                if current_room_id:
                    chat_message = message["text"]
                    sender = message["sender"]
                    with lock:
                        for player_conn in rooms[current_room_id]["players"]:
                            player_conn.send(json.dumps({"status": "new_message", "sender": sender, "text": chat_message}).encode("utf-8"))

    except Exception as e:
        print(f"Error with client {addr}: {e}")

    finally:
        # Clean up on disconnect
        if current_room_id:
            with lock:
                rooms[current_room_id]["players"].remove(conn)
                if not rooms[current_room_id]["players"]:
                    del rooms[current_room_id]
                else:
                    for player_conn in rooms[current_room_id]["players"]:
                        player_conn.send(json.dumps({"status": "player_left"}).encode("utf-8"))
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

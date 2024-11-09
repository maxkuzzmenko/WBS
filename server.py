import socket
import threading
import json
from random import randint

# Server Configuration
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5555
rooms = {}  # Format: { room_id: {"players": {conn: player_data}, "max_players": 5} }
lock = threading.Lock()

def broadcast_positions():
    while True:
        with lock:
            for room_id, room_data in rooms.items():
                players_data = {str(conn.getpeername()): data for conn, data in room_data["players"].items()}
                message = {"status": "update_players", "players": players_data}
                for conn in room_data["players"]:
                    try:
                        conn.send((json.dumps(message) + "\n").encode("utf-8"))
                    except Exception as e:
                        print(f"Error broadcasting to {conn}: {e}")

# Start broadcasting positions in a separate thread
broadcast_thread = threading.Thread(target=broadcast_positions, daemon=True)
broadcast_thread.start()

def handle_client(conn, addr):
    current_room_id = None
    buffer = ""
    try:
        while True:
            # Step 1: Receive data from client
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break
            buffer += data
            print(f"Data received from {addr}: {data}")

            # Step 2: Process each complete JSON message separated by newline
            while "\n" in buffer:
                message_str, buffer = buffer.split("\n", 1)
                try:
                    message = json.loads(message_str)
                    print(f"Parsed message from {addr}: {message}")
                except json.JSONDecodeError:
                    print("Received malformed JSON, skipping...")
                    continue

                # Step 3: Process 'create_room' action
                action = message.get("action")
                print(f"Action received: {action}")

                if action == "create_room":
                    print("Starting to create room...")

                    # Directly generate a room ID here
                    room_id = str(randint(1000, 9999))
                    print(f"Generated room ID: {room_id}")

                    # Attempt to acquire lock and add room to rooms dictionary
                    with lock:
                        rooms[room_id] = {"players": {conn: {"x": 100, "y": 500}}, "max_players": 5}
                        print(f"Room {room_id} created. Current rooms: {rooms}")

                    current_room_id = room_id
                    response = json.dumps({"status": "room_created", "room_id": room_id}) + "\n"
                    print(f"Preparing response for client {addr}")

                    # Step 4: Attempt to send the response back to the client
                    conn.send(response.encode("utf-8"))
                    print("Room creation response sent to client.")

                elif action == "join_room":
                    room_id = str(message.get("room_id"))  # Convert to string for consistency
                    with lock:
                        if room_id in rooms and len(rooms[room_id]["players"]) < rooms[room_id]["max_players"]:
                            rooms[room_id]["players"][conn] = {"x": 100, "y": 500}
                            current_room_id = room_id
                            conn.send(
                                (json.dumps({"status": "joined_room", "room_id": room_id}) + "\n").encode("utf-8"))
                            # Notify other players in the room
                            for player_conn in rooms[room_id]["players"]:
                                if player_conn != conn:
                                    player_conn.send((json.dumps({"status": "player_joined"}) + "\n").encode("utf-8"))
                            print(f"Client {addr} joined room {room_id}")
                        else:
                            conn.send((json.dumps(
                                {"status": "error", "message": "Room full or doesn't exist"}) + "\n").encode("utf-8"))

                elif action == "update_player_data" and current_room_id:
                    # Store player position updates
                    with lock:
                        if current_room_id in rooms and conn in rooms[current_room_id]["players"]:
                            rooms[current_room_id]["players"][conn] = message["player_data"]
                            print(f"Updated player data for {addr} in room {current_room_id}: {message['player_data']}")

    except Exception as e:
        print(f"Error with client {addr}: {e}")

    finally:
        # Clean up on disconnect
        if current_room_id:
            with lock:
                if current_room_id in rooms:
                    if conn in rooms[current_room_id]["players"]:
                        del rooms[current_room_id]["players"][conn]
                    if not rooms[current_room_id]["players"]:  # If room is empty, delete it
                        del rooms[current_room_id]
                    else:
                        for player_conn in rooms[current_room_id]["players"]:
                            player_conn.send((json.dumps({"status": "player_left"}) + "\n").encode("utf-8"))
        conn.close()
        print(f"Client {addr} disconnected")


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

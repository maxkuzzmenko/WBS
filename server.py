import socket
import threading
import json
from random import randint

# Server Configuration
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5555
rooms = {}  # Format: { room_id: {"players": {conn: player_data}, "max_players": 5, "player_count": 0} }
lock = threading.Lock()


def broadcast_positions():
    """Broadcast positions of all players in each room to all connected clients."""
    while True:
        with lock:
            for room_id, room_data in list(rooms.items()):  # Use list() to safely modify during iteration
                players_data = {
                    data["label"]: {"x": data["x"], "y": data["y"]}
                    for data in room_data["players"].values()
                }
                message = {"status": "update_players", "players": players_data}

                # Send updates to each player
                for conn in list(room_data["players"].keys()):  # Copy to list to allow safe modification
                    try:
                        conn.send((json.dumps(message) + "\n").encode("utf-8"))
                    except (BrokenPipeError, ConnectionResetError):
                        # Handle disconnection by removing client
                        print(f"Removing disconnected client: {conn}")
                        remove_client_from_room(conn, room_id)


def remove_client_from_room(conn, room_id):
    """Remove a client from the room and notify other players."""
    if room_id in rooms and conn in rooms[room_id]["players"]:
        player_label = rooms[room_id]["players"][conn]["label"]
        del rooms[room_id]["players"][conn]  # Remove client from room

        # Notify other players in the room about the disconnection
        for player_conn in rooms[room_id]["players"]:
            try:
                player_conn.send((json.dumps({"status": "player_left", "label": player_label}) + "\n").encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                print(f"Failed to notify a player about disconnection in room {room_id}")

        # If room is empty, delete it
        if not rooms[room_id]["players"]:
            del rooms[room_id]
            print(f"Room {room_id} deleted as it became empty.")


# Start broadcasting positions in a separate thread
broadcast_thread = threading.Thread(target=broadcast_positions, daemon=True)
broadcast_thread.start()


def handle_client(conn, addr):
    """Handle an individual client connection."""
    current_room_id = None
    buffer = ""
    try:
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break
            buffer += data

            while "\n" in buffer:
                message_str, buffer = buffer.split("\n", 1)
                try:
                    message = json.loads(message_str)
                except json.JSONDecodeError:
                    print("Received malformed JSON, skipping...")
                    continue

                action = message.get("action")
                if action != "update_player_data":
                    print(f"Action received: {action}")

                if action == "create_room":
                    room_id = str(randint(1000, 9999))
                    print(f"Generated room ID: {room_id}")

                    with lock:
                        rooms[room_id] = {"players": {}, "max_players": 5, "player_count": 0}

                    current_room_id = room_id
                    response = json.dumps({"status": "room_created", "room_id": room_id}) + "\n"
                    conn.send(response.encode("utf-8"))

                elif action == "join_room":
                    room_id = str(message.get("room_id"))
                    with lock:
                        if room_id in rooms and len(rooms[room_id]["players"]) < rooms[room_id]["max_players"]:
                            rooms[room_id]["player_count"] += 1
                            player_label = f"Player {rooms[room_id]['player_count']}"

                            rooms[room_id]["players"][conn] = {"label": player_label, "x": 100, "y": 500}
                            current_room_id = room_id
                            conn.send(
                                (json.dumps({"status": "joined_room", "room_id": room_id, "label": player_label}) + "\n").encode("utf-8"))

                            # Notify other players in the room about the new player
                            for player_conn in rooms[room_id]["players"]:
                                if player_conn != conn:
                                    player_conn.send((json.dumps({"status": "player_joined", "label": player_label}) + "\n").encode("utf-8"))
                            print(f"{player_label} ({addr}) joined room {room_id}")
                        else:
                            conn.send((json.dumps(
                                {"status": "error", "message": "Room full or doesn't exist"}) + "\n").encode("utf-8"))

                elif action == "update_player_data" and current_room_id:
                    with lock:
                        if current_room_id in rooms and conn in rooms[current_room_id]["players"]:
                            rooms[current_room_id]["players"][conn]["x"] = message["player_data"]["x"]
                            rooms[current_room_id]["players"][conn]["y"] = message["player_data"]["y"]

    except Exception as e:
        print(f"Error with client {addr}: {e}")

    finally:
        # Clean up client from room and close the connection
        if current_room_id:
            with lock:
                remove_client_from_room(conn, current_room_id)
        conn.close()
        print(f"Client {addr} disconnected")


def start_server():
    """Start the server and listen for incoming connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        conn, addr = server.accept()
        print(f"New connection: {addr}")
        threading.Thread(target=handle_client, args=(conn, addr)).start()


start_server()

import socket
import threading
import json
from random import randint

# Server Configuration
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5555
rooms = {}  # Format: { room_id: {"players": {conn: player_data}, "max_players": 5, "player_count": 0} }
lock = threading.Lock()

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
                    print(f"Parsed message from {addr}: {message}")
                except json.JSONDecodeError:
                    print("Received malformed JSON, skipping...")
                    continue

                action = message.get("action")
                print(f"Action received: {action}")

                if action == "create_room":
                    room_id = str(randint(1000, 9999))
                    print(f"Generated room ID: {room_id}")

                    with lock:
                        rooms[room_id] = {"players": {}, "max_players": 5, "player_count": 0}
                    current_room_id = room_id
                    response = json.dumps({"status": "room_created", "room_id": room_id}) + "\n"
                    conn.send(response.encode("utf-8"))
                    print("Room creation response sent to client.")

                elif action == "join_room":
                    room_id = str(message.get("room_id"))
                    print(f"Attempting to join room: {room_id}")

                    with lock:
                        if room_id in rooms and len(rooms[room_id]["players"]) < rooms[room_id]["max_players"]:
                            rooms[room_id]["player_count"] += 1
                            player_label = f"Player {rooms[room_id]['player_count']}"
                            player_color = "RED" if rooms[room_id]['player_count'] % 2 == 0 else "BLUE"
                            print(f"Assigning {player_label} to client {addr}")

                            rooms[room_id]["players"][conn] = {
                                "label": player_label, "x": 100, "y": 500, "color": player_color
                            }
                            current_room_id = room_id
                            conn.send(
                                (json.dumps({"status": "joined_room", "room_id": room_id, "label": player_label, "color": player_color}) + "\n").encode("utf-8"))
                            print(f"{player_label} ({addr}) joined room {room_id}")

                            # Notify all players in the room about the new player
                            for player_conn in rooms[room_id]["players"]:
                                if player_conn != conn:
                                    try:
                                        player_conn.send((json.dumps({
                                            "status": "player_joined",
                                            "label": player_label,
                                            "color": player_color,
                                            "x": 100,
                                            "y": 500
                                        }) + "\n").encode("utf-8"))
                                    except Exception as e:
                                        print(f"Error notifying player about new player: {e}")

                        else:
                            print(f"Room {room_id} is full or does not exist.")
                            conn.send((json.dumps(
                                {"status": "error", "message": "Room full or doesn't exist"}) + "\n").encode("utf-8"))

                elif action == "update_player_data" and current_room_id:
                    with lock:
                        if current_room_id in rooms and conn in rooms[current_room_id]["players"]:
                            rooms[current_room_id]["players"][conn]["x"] = message["player_data"]["x"]
                            rooms[current_room_id]["players"][conn]["y"] = message["player_data"]["y"]

                            # Notify other players about updated player positions
                            for player_conn in rooms[current_room_id]["players"]:
                                if player_conn != conn:
                                    try:
                                        player_conn.send((json.dumps({
                                            "status": "update_player_position",
                                            "label": rooms[current_room_id]["players"][conn]["label"],
                                            "x": message["player_data"]["x"],
                                            "y": message["player_data"]["y"]
                                        }) + "\n").encode("utf-8"))
                                    except Exception as e:
                                        print(f"Error updating player position: {e}")

    except Exception as e:
        print(f"Error with client {addr}: {e}")

    finally:
        # Remove player from room and close the connection
        if current_room_id:
            with lock:
                if current_room_id in rooms and conn in rooms[current_room_id]["players"]:
                    player_label = rooms[current_room_id]["players"][conn]["label"]
                    del rooms[current_room_id]["players"][conn]
                    if not rooms[current_room_id]["players"]:  # Delete room if empty
                        del rooms[current_room_id]
                    else:
                        for player_conn in rooms[current_room_id]["players"]:
                            try:
                                player_conn.send((json.dumps({"status": "player_left", "label": player_label}) + "\n").encode("utf-8"))
                            except Exception as e:
                                print(f"Error notifying player about disconnection: {e}")
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

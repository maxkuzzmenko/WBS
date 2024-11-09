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


# Handle each client connection
def handle_client(conn, addr):
    current_room_id = None
    buffer = ""  # Buffer to accumulate incoming data
    try:
        while True:
            # Receive message from client
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            # Accumulate data in buffer
            buffer += data

            # Process each complete JSON object (split by newline)
            while "\n" in buffer:
                message_str, buffer = buffer.split("\n", 1)  # Split at first newline
                try:
                    message = json.loads(message_str)
                except json.JSONDecodeError:
                    print("Received malformed JSON, skipping...")
                    continue

                action = message.get("action")

                if action == "create_room":
                    # Generate a unique room ID and create a new room
                    room_id = str(random.randint(1000, 9999))
                    with lock:
                        rooms[room_id] = {"players": [conn], "max_players": 5}
                    current_room_id = room_id
                    conn.send((json.dumps({"status": "room_created", "room_id": room_id}) + "\n").encode("utf-8"))

                elif action == "join_room":
                    room_id = message.get("room_id")
                    with lock:
                        if room_id in rooms and len(rooms[room_id]["players"]) < rooms[room_id]["max_players"]:
                            rooms[room_id]["players"].append(conn)
                            current_room_id = room_id
                            conn.send(
                                (json.dumps({"status": "joined_room", "room_id": room_id}) + "\n").encode("utf-8"))
                            # Notify all players in the room of the new player
                            for player_conn in rooms[room_id]["players"]:
                                if player_conn != conn:
                                    player_conn.send((json.dumps({"status": "player_joined"}) + "\n").encode("utf-8"))
                        else:
                            conn.send((json.dumps(
                                {"status": "error", "message": "Room full or doesn't exist"}) + "\n").encode("utf-8"))

                elif action == "send_message":
                    if current_room_id:
                        chat_message = message.get("text")
                        sender = message.get("sender")
                        with lock:
                            for player_conn in rooms[current_room_id]["players"]:
                                player_conn.send((json.dumps(
                                    {"status": "new_message", "sender": sender, "text": chat_message}) + "\n").encode(
                                    "utf-8"))

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
                        player_conn.send((json.dumps({"status": "player_left"}) + "\n").encode("utf-8"))
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

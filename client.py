import socket
import threading
import json

# Server connection configuration
SERVER_IP = "127.0.0.1"  # Change this to your server IP
SERVER_PORT = 5555

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if data:
                message = json.loads(data)
                print("Received:", message)
        except Exception as e:
            print("Connection error:", e)
            break

# Start receiving messages in a separate thread
threading.Thread(target=receive_messages, daemon=True).start()

# Function to create a room
def create_room():
    message = {"action": "create_room"}
    client_socket.send(json.dumps(message).encode("utf-8"))

# Function to join a room
def join_room(room_id):
    message = {"action": "join_room", "room_id": room_id}
    client_socket.send(json.dumps(message).encode("utf-8"))

# Main loop for user commands
while True:
    command = input("Enter 'create' to create a room or 'join <room_id>' to join a room: ")
    if command == "create":
        create_room()
    elif command.startswith("join"):
        room_id = command.split(" ")[1]
        join_room(room_id)

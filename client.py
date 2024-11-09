import socket
import threading
import json

# Server connection configuration
SERVER_IP = "0.tcp.eu.ngrok.io"  # Change this to your server IP
SERVER_PORT = 11094

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if data:
                message = json.loads(data)
                if message["status"] == "new_message":
                    print(f"{message['sender']}: {message['text']}")
                elif message["status"] == "player_joined":
                    print("A new player has joined the room.")
                elif message["status"] == "player_left":
                    print("A player has left the room.")
                else:
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

# Function to send a chat message
def send_chat_message(text, sender="Player"):
    message = {"action": "send_message", "text": text, "sender": sender}
    client_socket.send(json.dumps(message).encode("utf-8"))
# Main loop for user commands
while True:
    command = input("Enter a command ('create', 'join <room_id>', 'say <message>'): ")
    if command == "create":
        create_room()
    elif command.startswith("join"):
        room_id = command.split(" ")[1]
        join_room(room_id)
    elif command.startswith("say"):
        text = command.split(" ", 1)[1]
        send_chat_message(text)

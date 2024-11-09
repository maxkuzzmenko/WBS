import socket
import threading
import json
import pygame
import sys

# Server IP and Port (Use your server's public IP address and port here)
SERVER_IP = "0.tcp.eu.ngrok.io"
SERVER_PORT = 11094

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 75
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Screen and Clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game with Network Multiplayer and Chat")
clock = pygame.time.Clock()

# Player properties
player_size = (50, 50)
gravity = 1
jump_height = -15
dash_speed = 15
dash_cooldown = 30
player_speed = 5

# Initial player data for this client
player_data = {
    "x": 100,
    "y": 500,
    "health": 100,
    "color": "BLUE",
    "velocity": 0,
    "on_ground": False,
    "double_jump_allowed": True,
    "dash_timer": 0,
    "is_slashing": False,
    "slash_timer": 0
}
other_players = {}
current_room_id = None

# Platform properties
platforms = [pygame.Rect(0, 550, 800, 10)]

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))


# Function to receive messages from the server
def receive_messages():
    global other_players
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if data:
                message = json.loads(data)

                # Handle different types of messages from the server
                if message["status"] == "new_message":
                    print(f"{message['sender']}: {message['text']}")
                elif message["status"] == "player_joined":
                    print("A new player has joined the room.")
                elif message["status"] == "player_left":
                    print("A player has left the room.")
                elif message["status"] == "room_created":
                    global current_room_id
                    current_room_id = message["room_id"]
                    print(f"Room created. Room ID: {current_room_id}")
                elif message["status"] == "joined_room":
                    current_room_id = message["room_id"]
                    print(f"Joined room: {current_room_id}")
                elif message["status"] == "update_players":
                    other_players = message["players"]
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


# Function to send player data to the server
def send_data():
    while True:
        try:
            if current_room_id:
                player_data_message = {
                    "action": "update_player_data",
                    "room_id": current_room_id,
                    "player_data": player_data
                }
                client_socket.send(json.dumps(player_data_message).encode("utf-8"))
        except:
            break


# Start sending player data in a separate thread
threading.Thread(target=send_data, daemon=True).start()


# Game logic for player movement
def handle_player_movement(keys_pressed):
    global player_data

    # Horizontal movement
    if keys_pressed[pygame.K_a]:  # Left
        player_data["x"] -= player_speed
    if keys_pressed[pygame.K_d]:  # Right
        player_data["x"] += player_speed

    # Jump and double jump
    if keys_pressed[pygame.K_w]:
        if player_data["on_ground"]:
            player_data["velocity"] = jump_height
            player_data["on_ground"] = False
            player_data["double_jump_allowed"] = True
        elif player_data["double_jump_allowed"]:
            player_data["velocity"] = jump_height
            player_data["double_jump_allowed"] = False

    # Dash
    if keys_pressed[pygame.K_LSHIFT] and player_data["dash_timer"] == 0:
        dash_direction = player_speed if keys_pressed[pygame.K_d] else -player_speed
        player_data["x"] += dash_direction * dash_speed
        player_data["dash_timer"] = dash_cooldown

    # Gravity and vertical movement
    player_data["velocity"] += gravity
    player_data["y"] += player_data["velocity"]

    # Collision detection with platforms
    player_rect = pygame.Rect(player_data["x"], player_data["y"], *player_size)
    for platform in platforms:
        if player_rect.colliderect(platform) and player_data["velocity"] > 0:
            player_data["y"] = platform.top - player_size[1]
            player_data["velocity"] = 0
            player_data["on_ground"] = True

    # Dash cooldown
    if player_data["dash_timer"] > 0:
        player_data["dash_timer"] -= 1


# Draw platforms, local player, and health bar
def draw_platforms():
    for platform in platforms:
        pygame.draw.rect(screen, GREEN, platform)


def draw_health_bar():
    pygame.draw.rect(screen, BLACK, (10, 10, 104, 24))
    pygame.draw.rect(screen, BLUE, (12, 12, player_data["health"], 20))


# Main game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement and interactions
    keys_pressed = pygame.key.get_pressed()
    handle_player_movement(keys_pressed)

    # Draw platforms, local player, and health bar
    draw_platforms()
    pygame.draw.rect(screen, BLUE, (player_data["x"], player_data["y"], *player_size))
    draw_health_bar()

    # Draw other players
    for pid, pdata in other_players.items():
        if pid != str(client_socket.getsockname()[1]):  # Don't draw self
            color = RED if pdata["color"] == "RED" else BLUE
            pygame.draw.rect(screen, color, (pdata["x"], pdata["y"], *player_size))

    pygame.display.flip()

pygame.quit()
client_socket.close()

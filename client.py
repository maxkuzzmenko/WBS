import socket
import threading
import json
import pygame
import sys

# Server IP and Port (replace with server's public IP if hosting remotely)
SERVER_IP = "192.168.1.129"
SERVER_PORT = 5555

# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
player_color = (0, 0, 255)
player_size = (50, 50)
gravity = 1
jump_height = -15
player_speed = 5
dash_speed = 15

# Player State
player_data = {"x": 100, "y": 500, "health": 100}
other_players = {}  # Stores other players' states

# Connect to Server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Function to send data to the server
def send_data():
    while True:
        try:
            client_socket.send(json.dumps(player_data).encode("utf-8"))
        except:
            break

# Function to receive data from the server
def receive_data():
    global other_players
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if data:
                other_players = json.loads(data)
        except:
            break

# Start threads to handle sending and receiving data
threading.Thread(target=send_data, daemon=True).start()
threading.Thread(target=receive_data, daemon=True).start()

# Game Loop
running = True
on_ground = False
velocity = 0
double_jump_allowed = True

while running:
    clock.tick(60)
    screen.fill((255, 255, 255))

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_data["x"] -= player_speed
    if keys[pygame.K_RIGHT]:
        player_data["x"] += player_speed
    if keys[pygame.K_SPACE]:
        if on_ground:
            velocity = jump_height
            on_ground = False
            double_jump_allowed = True
        elif double_jump_allowed:
            velocity = jump_height
            double_jump_allowed = False

    # Gravity and Collision
    velocity += gravity
    player_data["y"] += velocity

    if player_data["y"] >= 500:
        player_data["y"] = 500
        velocity = 0
        on_ground = True

    # Draw Local Player
    pygame.draw.rect(screen, player_color, (player_data["x"], player_data["y"], *player_size))

    # Draw Other Players
    for pid, pdata in other_players.items():
        if pid != str(client_socket.getsockname()[1]):  # Avoid drawing self
            pygame.draw.rect(screen, (255, 0, 0), (pdata["x"], pdata["y"], *player_size))

    pygame.display.flip()

pygame.quit()
client_socket.close()

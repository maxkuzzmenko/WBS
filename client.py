import socket
import threading
import json
import pygame
import sys

# Server IP and Port (Replace with server's IP for global access)
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555

# Player data
player_data = {
    "x": 100,
    "y": 500,
    "health": 100,
}

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
player_color = (0, 0, 255)
player_speed = 5
other_players = {}

# Socket connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Function to send data to the server
def send_data():
    while True:
        try:
            # Send current player data
            client_socket.send(json.dumps(player_data).encode("utf-8"))
        except:
            print("[ERROR] Lost connection to the server.")
            client_socket.close()
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
            print("[ERROR] Lost connection to the server.")
            client_socket.close()
            break

# Start threads to send and receive data
threading.Thread(target=send_data, daemon=True).start()
threading.Thread(target=receive_data, daemon=True).start()

# Game loop
running = True
while running:
    clock.tick(30)
    screen.fill((255, 255, 255))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_data["x"] -= player_speed
    if keys[pygame.K_RIGHT]:
        player_data["x"] += player_speed
    if keys[pygame.K_UP]:
        player_data["y"] -= player_speed
    if keys[pygame.K_DOWN]:
        player_data["y"] += player_speed

    # Draw the local player
    pygame.draw.rect(screen, player_color, (player_data["x"], player_data["y"], 50, 50))

    # Draw other players
    for pid, pdata in other_players.items():
        if pid != player_data.get("id"):  # Don't draw self
            pygame.draw.rect(screen, (255, 0, 0), (pdata["x"], pdata["y"], 50, 50))

    pygame.display.flip()

pygame.quit()
client_socket.close()

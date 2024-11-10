import socket
import threading
import json
import pygame
import sys

# Server IP and Port (Replace with your server’s ngrok URL and port)
SERVER_IP = "192.168.1.129"
SERVER_PORT = 5555

# Initialize pygame
pygame.init()

# Screen Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Screen and Clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Platformer")
clock = pygame.time.Clock()

# Player properties
player_size = (50, 50)
player_speed = 5
gravity = 1
jump_height = -15

# Initial player data for this client
player_data = {
    "x": 100,
    "y": 500,
    "color": "BLUE",
    "velocity": 0,
    "on_ground": False,
    "double_jump_allowed": True,
}
other_players = {}  # Other players' data
current_room_id = None  # Room ID for this player

# Socket setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))


# Function to receive messages from the server
def receive_messages():
    global other_players
    buffer = ""
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break

            buffer += data  # Add new data to buffer

            # Process each complete JSON message
            while "\n" in buffer:
                message_str, buffer = buffer.split("\n", 1)  # Split at first newline
                try:
                    message = json.loads(message_str)
                except json.JSONDecodeError:
                    print("Received malformed JSON, skipping...")
                    continue

                # Handle different message types
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
                    # Update `other_players` with the received players' positions
                    other_players = message["players"]
                    print("Updated player positions:", other_players)  # Debug print
        except Exception as e:
            print("Connection error:", e)
            break



# Start receiving messages in a separate thread
threading.Thread(target=receive_messages, daemon=True).start()


# Function to create a room
def create_room():
    message = {"action": "create_room"}
    client_socket.send((json.dumps(message) + "\n").encode("utf-8"))  # Send message with newline
    print("Sent create_room request to server.")


# Function to join a room
def join_room(room_id):
    message = {"action": "join_room", "room_id": room_id}
    client_socket.send((json.dumps(message) + "\n").encode("utf-8"))  # Send message with newline
    print("Sent join_room request to server.")


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
                client_socket.send((json.dumps(player_data_message) + "\n").encode("utf-8"))
        except Exception as e:
            print("Error sending data:", e)
            break


# Start sending player data in a separate thread
threading.Thread(target=send_data, daemon=True).start()


# Display the main menu for room creation and joining
def main_menu():
    menu_font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(300, 250, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ""
    menu_message = "Enter 'create' to create a room or Room ID to join"

    while True:
        screen.fill(WHITE)
        menu_text = menu_font.render(menu_message, True, BLACK)
        screen.blit(menu_text, (150, 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle the input box
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text.lower() == "create":
                            create_room()
                        else:
                            join_room(text)
                        text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        txt_surface = menu_font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

        # Exit the menu once we've joined or created a room
        if current_room_id:
            break


# Player movement
def handle_player_movement(keys_pressed):
    global player_data
    if keys_pressed[pygame.K_a]:  # Move left
        player_data["x"] -= player_speed
    if keys_pressed[pygame.K_d]:  # Move right
        player_data["x"] += player_speed
    if keys_pressed[pygame.K_w]:  # Jump
        if player_data["on_ground"]:
            player_data["velocity"] = jump_height
            player_data["on_ground"] = False
            player_data["double_jump_allowed"] = True
        elif player_data["double_jump_allowed"]:
            player_data["velocity"] = jump_height
            player_data["double_jump_allowed"] = False
    player_data["velocity"] += gravity
    player_data["y"] += player_data["velocity"]

    # Ground collision
    if player_data["y"] > 500:
        player_data["y"] = 500
        player_data["on_ground"] = True
        player_data["velocity"] = 0


# Draw all players on the screen
def draw_players():
    # Draw this client's player
    pygame.draw.rect(screen, BLUE, (player_data["x"], player_data["y"], *player_size))

    # Draw other players
    for player_id, pdata in other_players.items():
        if player_id != str(client_socket.getsockname()[1]):  # Avoid drawing this client twice
            color = RED if pdata["color"] == "RED" else BLUE
            pygame.draw.rect(screen, color, (pdata["x"], pdata["y"], *player_size))


# Game Loop
def game_loop():
    while True:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get player input
        keys_pressed = pygame.key.get_pressed()
        handle_player_movement(keys_pressed)

        # Draw elements on the screen
        draw_players()

        pygame.display.flip()
        clock.tick(FPS)


# Main Program Flow
main_menu()
game_loop()

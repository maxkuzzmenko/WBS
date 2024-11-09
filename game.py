import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Screen and Clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game with Multiplayer")
clock = pygame.time.Clock()

# Player properties
player_size = (50, 50)
gravity = 1
jump_height = -15
dash_speed = 15
dash_cooldown = 30
damage_cooldown = 30

# Initial player positions and controls
players = [
    {  # Player 1
        "color": BLUE,
        "position": [100, 500],
        "velocity": 0,
        "speed": 5,
        "health": 100,
        "double_jump_allowed": True,
        "dash_timer": 0,
        "damage_timer": 0,
        "is_slashing": False,
        "slash_timer": 0,
        "controls": {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "dash": pygame.K_LSHIFT,
            "slash": pygame.K_f,
            "down":pygame.K_s
        }
    },
    {  # Player 2
        "color": RED,
        "position": [200, 500],
        "velocity": 0,
        "speed": 5,
        "health": 100,
        "double_jump_allowed": True,
        "dash_timer": 0,
        "damage_timer": 0,
        "is_slashing": False,
        "slash_timer": 0,
        "controls": {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "dash": pygame.K_RSHIFT,
            "slash": pygame.K_RETURN,
            "down":pygame.K_DOWN
        }
    }
]

# Platform properties
platforms = [
    pygame.Rect(0, 550, 800, 10),
#    pygame.Rect(400, 400, 200, 10),
#    pygame.Rect(600, 300, 200, 10)
]

# Enemy properties
enemy_size = (40, 40)
enemy_speed = 2
initial_enemies = [
    {'rect': pygame.Rect(150, 510, *enemy_size), 'direction': 1, 'platform': platforms[0]},
#    {'rect': pygame.Rect(450, 360, *enemy_size), 'direction': 1, 'platform': platforms[1]},
#    {'rect': pygame.Rect(650, 260, *enemy_size), 'direction': 1, 'platform': platforms[2]}
]
enemies = [enemy.copy() for enemy in initial_enemies]


def reset_game():
    global enemies
    for player in players:
        player["position"] = [100, 500] if player["color"] == BLUE else [200, 500]
        player["health"] = 100
        player["velocity"] = 0
        player["double_jump_allowed"] = True
        player["dash_timer"] = 0
        player["damage_timer"] = 0
        player["is_slashing"] = False
        player["slash_timer"] = 0
    enemies = [enemy.copy() for enemy in initial_enemies]


def draw_platforms():
    for platform in platforms:
        pygame.draw.rect(screen, GREEN, platform)


def handle_player_movement(player, keys_pressed):
    # Horizontal movement
    if keys_pressed[player["controls"]["left"]]:
        player["position"][0] -= player["speed"]
    if keys_pressed[player["controls"]["right"]]:
        player["position"][0] += player["speed"]

    # Jump and double jump
    if keys_pressed[player["controls"]["jump"]]:
        if player["on_ground"]:
            player["velocity"] = jump_height
            player["on_ground"] = False
            player["double_jump_allowed"] = True
        elif player["double_jump_allowed"]:
            player["velocity"] = jump_height
            player["double_jump_allowed"] = False

    # Dash
    if keys_pressed[player["controls"]["dash"]] and player["dash_timer"] == 0:
        dash_direction = player["speed"] if keys_pressed[player["controls"]["right"]] else -player["speed"]
        player["position"][0] += dash_direction * dash_speed
        player["dash_timer"] = dash_cooldown

    # Slash attack
    if keys_pressed[player["controls"]["slash"]] and not player["is_slashing"]:
        player["is_slashing"] = True
        player["slash_timer"] = 10

    # Handle slash timer countdown
    if player["is_slashing"]:
        player["slash_timer"] -= 1
        if player["slash_timer"] <= 0:
            player["is_slashing"] = False

    # Gravity and vertical movement
    player["velocity"] += gravity
    player["position"][1] += player["velocity"]

    # Collision detection with platforms
    player["on_ground"] = False
    player_rect = pygame.Rect(player["position"][0], player["position"][1], *player_size)
    for platform in platforms:
        if player_rect.colliderect(platform) and player["velocity"] > 0:
            player["position"][1] = platform.top - player_size[1]
            player["velocity"] = 0
            player["on_ground"] = True

    # Dash cooldown
    if player["dash_timer"] > 0:
        player["dash_timer"] -= 1


def handle_enemies():
    for enemy in enemies:
        enemy_rect = enemy['rect']
        platform = enemy['platform']

        # Move enemy back and forth
        enemy_rect.x += enemy_speed * enemy['direction']

        # Reverse direction if the enemy hits the edge of the platform
        if enemy_rect.left <= platform.left or enemy_rect.right >= platform.right:
            enemy['direction'] *= -1

        # Check for collision with each player
        for player in players:
            player_rect = pygame.Rect(player["position"][0], player["position"][1], *player_size)
            if player_rect.colliderect(enemy_rect):
                if player["is_slashing"]:
                    enemies.remove(enemy)  # Remove enemy if hit by slash
                elif player["damage_timer"] == 0:
#                    player["health"] -= 10  # Reduce health if enemy touches player
                    player["damage_timer"] = damage_cooldown  # Reset damage cooldown

    # Decrease each player's damage cooldown timer
    for player in players:
        if player["damage_timer"] > 0:
            player["damage_timer"] -= 1


def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, BLACK, enemy['rect'])


def draw_health_bars():
    for i, player in enumerate(players):
        health_color = player["color"]
        pygame.draw.rect(screen, BLACK, (10 + i * 120, 10, 104, 24))
        pygame.draw.rect(screen, health_color, (12 + i * 120, 12, player["health"], 20))


def draw_game_over_screen():
    game_over_font = pygame.font.Font(None, 72)
    game_over_text = game_over_font.render("Game Over", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))


# Main game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

    # Check for game over
    if any(player["health"] <= 0 for player in players):
        draw_game_over_screen()
    else:
        # Player movement and interactions
        keys_pressed = pygame.key.get_pressed()
        for player in players:
            handle_player_movement(player, keys_pressed)

        # Enemy movement and interactions
        handle_enemies()

        # Draw players, platforms, enemies, and health bars
        for player in players:
            pygame.draw.rect(screen, player["color"], (*player["position"], *player_size))
        draw_platforms()
        draw_enemies()
        draw_health_bars()

        # Display slash visual feedback
        for player in players:
            if player["is_slashing"]:
                slash_rect = pygame.Rect(player["position"][0] - 10, player["position"][1], player_size[0] + 20,
                                         player_size[1])
                pygame.draw.rect(screen, (200, 200, 255), slash_rect, 3)

    pygame.display.flip()

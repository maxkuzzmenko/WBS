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
PURPLE = (255, 0, 255)  # Color for spike platforms

# Screen and Clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Game")
clock = pygame.time.Clock()

# Player properties
player_size = (50, 50)
player_color = BLUE
initial_player_pos = [100, 500]
player_pos = initial_player_pos[:]
player_velocity = 0
player_speed = 5
dash_speed = 15
dash_cooldown = 30
gravity = 1
jump_height = -15
double_jump_allowed = True
dash_timer = 0
on_ground = False
is_slashing = False
slash_timer = 0
slash_duration = 10
player_health = 100
damage_cooldown = 30
damage_timer = 0
player_facing_right = True  # Default facing direction is right

# Regular platform properties
platforms = [
    pygame.Rect(0, 500, 200, 100),
    pygame.Rect(300, 400, 200, 200),
    pygame.Rect(600, 300, 200, 300),
]

# Enemy properties
enemy_size = (40, 40)
enemy_speed = 2
initial_enemies = [
    {'rect': pygame.Rect(150, 460, *enemy_size), 'direction': 1, 'platform': platforms[0]},
    {'rect': pygame.Rect(450, 360, *enemy_size), 'direction': 1, 'platform': platforms[1]},
    {'rect': pygame.Rect(650, 260, *enemy_size), 'direction': 1, 'platform': platforms[2]}
]
enemies = [enemy.copy() for enemy in initial_enemies]

# Load and scale the player image
player_image = pygame.image.load("character images/cwayz dino nugget.png")  # Replace with your image file name
player_image = pygame.transform.scale(player_image, player_size)
enemy_image = pygame.image.load("character images/enemy_v.2.png")  # Replace with your enemy image
enemy_image = pygame.transform.scale(enemy_image, enemy_size)

# Spike platform properties
spike_platforms = [
    pygame.Rect(200, 550, 100, 10),  # Example of a spike platform
    pygame.Rect(500, 450, 100, 10)  # Another spike platform
]


def reset_game():
    global player_pos, player_health, enemies, player_velocity, damage_timer, is_slashing, dash_timer, double_jump_allowed
    player_pos = initial_player_pos[:]
    player_health = 100
    player_velocity = 0
    damage_timer = 0
    is_slashing = False
    dash_timer = 0
    double_jump_allowed = True
    enemies = [enemy.copy() for enemy in initial_enemies]


def draw_platforms():
    for platform in platforms:
        pygame.draw.rect(screen, BLUE, platform)


def draw_spike_platforms():
    for spike in spike_platforms:
        pygame.draw.rect(screen, PURPLE, spike)


def handle_player_movement(keys_pressed):
    global player_velocity, on_ground, is_slashing, slash_timer, double_jump_allowed, dash_timer, player_facing_right

    # Horizontal movement
    if keys_pressed[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= player_speed
        player_facing_right = False  # Facing left
    if keys_pressed[pygame.K_RIGHT] and player_pos[0] < WIDTH - player_size[0]:
        player_pos[0] += player_speed
        player_facing_right = True  # Facing right

    # Jump and double jump
    if keys_pressed[pygame.K_SPACE]:
        if on_ground:
            player_velocity = jump_height
            on_ground = False

    # Dash
    if keys_pressed[pygame.K_d] and dash_timer == 0:
        dash_direction = player_speed if keys_pressed[pygame.K_RIGHT] else -player_speed
        player_pos[0] += dash_direction * dash_speed
        dash_timer = dash_cooldown

    # Slash attack
    if keys_pressed[pygame.K_z] and not is_slashing:
        is_slashing = True
        slash_timer = slash_duration

    # Handle slash timer countdown
    if is_slashing:
        slash_timer -= 1
        if slash_timer <= 0:
            is_slashing = False

    # Gravity and vertical movement
    player_velocity += gravity
    player_pos[1] += player_velocity

    # Collision detection with platforms
    on_ground = False
    player_rect = pygame.Rect(player_pos[0], player_pos[1], *player_size)
    for platform in platforms:
        if player_rect.colliderect(platform) and player_velocity > 0:
            player_pos[1] = platform.top - player_size[1]
            player_velocity = 0
            on_ground = True

    # Collision detection with spike platforms (reset the game if touched)
    for spike in spike_platforms:
        if player_rect.colliderect(spike):
            player_health = 0

    # Dash cooldown
    if dash_timer > 0:
        dash_timer -= 1


def handle_enemies():
    global player_health, damage_timer

    for enemy in enemies:
        enemy_rect = enemy['rect']
        platform = enemy['platform']

        # Move enemy back and forth
        enemy_rect.x += enemy_speed * enemy['direction']

        # Reverse direction if the enemy hits the edge of the platform
        if enemy_rect.left <= platform.left or enemy_rect.right >= platform.right:
            enemy['direction'] *= -1

        # Check for collision with player
        player_rect = pygame.Rect(player_pos[0], player_pos[1], *player_size)
        if player_rect.colliderect(enemy_rect):
            if is_slashing:
                enemies.remove(enemy)  # Remove enemy if hit by slash
            elif damage_timer == 0:
                player_health -= 10  # Reduce health if enemy touches player
                damage_timer = damage_cooldown  # Reset damage cooldown

    # Decrease damage cooldown timer
    if damage_timer > 0:
        damage_timer -= 1


def draw_enemies():
    for enemy in enemies:
        enemy_rect = enemy['rect']
        # Flip the enemy image based on the direction they are facing
        flipped_enemy_image = enemy_image
        if enemy['direction'] == -1:  # If enemy is moving left, flip the image
            flipped_enemy_image = pygame.transform.flip(enemy_image, True, False)

        screen.blit(flipped_enemy_image, enemy_rect)  # Draw the flipped image or original image


def draw_health_bar():
    pygame.draw.rect(screen, BLACK, (10, 10, 104, 24))
    pygame.draw.rect(screen, RED, (12, 12, player_health, 20))


def draw_game_over_screen():
    game_over_font = pygame.font.Font(None, 72)
    game_over_text = game_over_font.render("Game Over", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))


# Main game loop
paused = False

running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_s:
                paused = not paused  # Toggle paused state

    # Pause logic
    if paused:
        # Display a "Paused" message on the screen
        paused_font = pygame.font.Font(None, 72)
        paused_text = paused_font.render("Paused", True, BLACK)
        screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 50))
        pygame.display.flip()
        continue  # Skip the rest of the game logic when paused

    # Check for game over
    if player_health <= 0:
        draw_game_over_screen()
    else:
        # Player movement
        keys_pressed = pygame.key.get_pressed()
        handle_player_movement(keys_pressed)

        # Enemy movement and interaction
        handle_enemies()

        # Draw platforms, enemies, health bar, and player
        draw_platforms()
        draw_spike_platforms()  # Draw spike platforms
        draw_enemies()  # Draw enemies with their textures
        draw_health_bar()

        # Replace rectangle with the player image, flipped if needed
        if player_facing_right:
            screen.blit(player_image, player_pos)
        else:
            flipped_image = pygame.transform.flip(player_image, True, False)  # Flip horizontally
            screen.blit(flipped_image, player_pos)

        # Display slash visual feedback
        if is_slashing:
            slash_rect = pygame.Rect(player_pos[0] - 10, player_pos[1], player_size[0] + 20, player_size[1])
            pygame.draw.rect(screen, (200, 200, 255), slash_rect, 3)

    pygame.display.flip()

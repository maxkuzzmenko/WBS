import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 75
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Screen and Clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game with Enemies")
clock = pygame.time.Clock()

# Player properties
player_size = (50, 50)
player_color = BLUE
player_pos = [100, 500]
player_velocity = 0
player_speed = 5
gravity = 1
jump_height = -20
on_ground = False
is_slashing = False
slash_timer = 0
slash_duration = 10  # Number of frames the slash lasts

# Platform properties
platforms = [
    pygame.Rect(100, 550, 200, 10),
    pygame.Rect(400, 400, 200, 10),
    pygame.Rect(600, 300, 200, 10)
]

# Enemy properties
enemy_size = (40, 40)
enemy_speed = 2
enemies = [
    {'rect': pygame.Rect(150, 510, *enemy_size), 'direction': 1, 'platform': platforms[0]},
    {'rect': pygame.Rect(450, 360, *enemy_size), 'direction': 1, 'platform': platforms[1]},
    {'rect': pygame.Rect(650, 260, *enemy_size), 'direction': 1, 'platform': platforms[2]}
]


def draw_platforms():
    for platform in platforms:
        pygame.draw.rect(screen, RED, platform)


def handle_player_movement(keys_pressed):
    global player_velocity, on_ground, is_slashing, slash_timer

    if keys_pressed[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys_pressed[pygame.K_RIGHT] and player_pos[0] < WIDTH - player_size[0]:
        player_pos[0] += player_speed

    # Jump
    if keys_pressed[pygame.K_SPACE] and on_ground:
        player_velocity = jump_height
        on_ground = False

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


def handle_enemies():
    for enemy in enemies:
        enemy_rect = enemy['rect']
        platform = enemy['platform']

        # Move enemy back and forth
        enemy_rect.x += enemy_speed * enemy['direction']

        # Reverse direction if the enemy hits the edge of the platform
        if enemy_rect.left <= platform.left or enemy_rect.right >= platform.right:
            enemy['direction'] *= -1

        # Check for collision with player attack
        player_rect = pygame.Rect(player_pos[0], player_pos[1], *player_size)
        if is_slashing and player_rect.colliderect(enemy_rect):
            enemies.remove(enemy)  # Remove enemy if hit by slash


def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, GREEN, enemy['rect'])


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

    # Player movement
    keys_pressed = pygame.key.get_pressed()
    handle_player_movement(keys_pressed)

    # Enemy movement and interaction
    handle_enemies()

    # Draw player and platforms
    pygame.draw.rect(screen, player_color, (*player_pos, *player_size))
    draw_platforms()
    draw_enemies()

    # Display slash visual feedback
    if is_slashing:
        slash_rect = pygame.Rect(player_pos[0] - 10, player_pos[1], player_size[0] + 20, player_size[1])
        pygame.draw.rect(screen, (200, 200, 255), slash_rect, 3)

    pygame.display.flip()

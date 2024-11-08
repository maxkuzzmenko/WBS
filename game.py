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

# Screen and Clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

# Player properties
player_size = (50, 50)
player_color = BLUE
player_pos = [100, 500]
player_velocity = 0
player_speed = 5
gravity = 1
jump_height = -15
on_ground = False

# Platform properties
platforms = [
    pygame.Rect(100, 550, 200, 10),
    pygame.Rect(400, 400, 200, 10),
    pygame.Rect(600, 300, 200, 10)
]

def draw_platforms():
    for platform in platforms:
        pygame.draw.rect(screen, RED, platform)

def handle_player_movement(keys_pressed):
    global player_velocity, on_ground

    if keys_pressed[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys_pressed[pygame.K_RIGHT] and player_pos[0] < WIDTH - player_size[0]:
        player_pos[0] += player_speed

    # Jump
    if keys_pressed[pygame.K_SPACE] and on_ground:
        player_velocity = jump_height
        on_ground = False

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

    # Draw player and platforms
    pygame.draw.rect(screen, player_color, (*player_pos, *player_size))
    draw_platforms()

    pygame.display.flip()

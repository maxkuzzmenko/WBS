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
pygame.display.set_caption("Joe: te Game")
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

# Regular platform properties (for first level)
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
enemy_image = pygame.image.load("character images/enemy.png")  # Replace with your enemy image
enemy_image = pygame.transform.scale(enemy_image, enemy_size)
player_dash_image = pygame.image.load("character images/dinodashnr.1.png")
player_dash_image = pygame.transform.scale(player_dash_image, player_size)
background_image = pygame.image.load("envpic/hintergrund_v.2.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
platform_texture_top = pygame.image.load("envpic/stein_oben_v.4png.png")
platform_texture_bottom = pygame.image.load("envpic/stein_connecting_v.2.png")
platform_width_top = platform_texture_top.get_width()
platform_width_bottom = platform_texture_bottom.get_width()
platform_height_bottom = platform_texture_bottom.get_height()




# Spike platform properties (for first level)
spike_platforms = [
    pygame.Rect(500, 450, 100, 10)  # Another spike platform
]

fake_spike_platforms = [
    pygame.Rect(200, 550, 100, 10)  # Example of a fake spike platform
]

# Second level properties
second_level_platforms = [
    pygame.Rect(0, 550, 800, 50),
    pygame.Rect(300, 450, 200, 50),
    pygame.Rect(600, 350, 200, 50),
    pygame.Rect(300, 200, 200, 50),
]

# Second level enemies and spikes
second_level_enemies = [
    {'rect': pygame.Rect(0, 460, *enemy_size), 'direction': 1, 'platform': second_level_platforms[0]},
    {'rect': pygame.Rect(450, 360, *enemy_size), 'direction': 1, 'platform': second_level_platforms[1]},
    {'rect': pygame.Rect(650, 260, *enemy_size), 'direction': 1, 'platform': second_level_platforms[2]}
]

second_level_spike_platforms = [
    pygame.Rect(500, 250, 100, 10),
    pygame.Rect(200, 150, 100, 10)
]

# Reset the game (for both levels)
def reset_game():
    global player_pos, player_health, enemies, player_velocity, damage_timer, is_slashing, dash_timer, double_jump_allowed, spike_platforms
    player_pos = initial_player_pos[:]
    player_health = 100
    player_velocity = 0
    damage_timer = 0
    is_slashing = False
    dash_timer = 0
    double_jump_allowed = True
    enemies = [enemy.copy() for enemy in initial_enemies]
    spike_platforms = [
        pygame.Rect(500, 450, 100, 10)  # Reset the spike platforms for the first level
    ]

# Handle the second level (set up new enemies and spikes)
def handle_second_level():
    global enemies, spike_platforms
    enemies = [enemy.copy() for enemy in second_level_enemies]  # Spawn second level enemies
    spike_platforms = second_level_spike_platforms  # Spawn second level spikes



# Draw second level platforms and spikes
def draw_second_level():
    for platform in second_level_platforms:
        pygame.draw.rect(screen, GREEN, platform)
    for spike in second_level_spike_platforms:
        pygame.draw.rect(screen, PURPLE, spike)
#     screen.blit("")


def draw_platforms():
    for platform in platforms:
        # Draw the top texture across the width of the platform
        for i in range(platform.width // platform_width_top):
            screen.blit(platform_texture_top, (platform.x + i * platform_width_top, platform.y))

        # Draw the bottom/base texture from the bottom up to just below the top layer
        for i in range(platform.width // platform_width_bottom):
            for j in range((platform.height - platform_height_bottom) // platform_height_bottom):
                # Ensure the bottom texture fills up from the bottom, up to the top layer
                screen.blit(platform_texture_bottom, (platform.x + i * platform_width_bottom,
                                                      platform.y + platform.height - (j + 1) * platform_height_bottom))


def draw_spike_platforms():
    for spike in spike_platforms:
        pygame.draw.rect(screen, PURPLE, spike)

def draw_fake_spike_platforms():
    for fake_spikes in fake_spike_platforms:  # Corrected this line
        pygame.draw.rect(screen, PURPLE, fake_spikes)

# Handle player movement
def handle_player_movement(keys_pressed):
    global player_velocity, on_ground, is_slashing, slash_timer, double_jump_allowed, dash_timer, player_facing_right, player_health

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
        elif double_jump_allowed:
            player_velocity = jump_height
            double_jump_allowed = False  # Disable further jumps

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
            double_jump_allowed = True  # Allow for double jump again when landing on platform

    # Collision detection with spike platforms (reset the game if touched)
    for spike in spike_platforms:
        if player_rect.colliderect(spike or second_level_spike_platforms):
            player_health -= 200

    # Collision detection with fake spike platforms (take damage, but don't reset the game)
    for fake_spike in fake_spike_platforms:
        if player_rect.colliderect(fake_spike):
            player_health -= 5  # Take lesser damage on fake spikes

    # Dash cooldown
    if dash_timer > 0:
        dash_timer -= 1

    if player_pos[1] < 0 or player_pos[1] > 750:
        player_health -= 150

# Handle enemies
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
                player_health -= 20  # Reduce health if enemy touches player
                damage_timer = damage_cooldown  # Reset damage cooldown

    # Decrease damage cooldown timer
    if damage_timer > 0:
        damage_timer -= 1


# Draw enemies
def draw_enemies():
    for enemy in enemies:
        enemy_rect = enemy['rect']
        # Flip the enemy image based on the direction they are facing
        flipped_enemy_image = enemy_image
        if enemy['direction'] == -1:  # If enemy is moving left, flip the image
            flipped_enemy_image = pygame.transform.flip(enemy_image, True, False)

        screen.blit(flipped_enemy_image, enemy_rect)  # Draw the flipped image or original image

# Draw health bar
def draw_health_bar():
    # Draw the background of the health bar
    pygame.draw.rect(screen, BLACK, (10, 10, 104, 24))

    # Draw the current health bar (colored red)
    pygame.draw.rect(screen, RED, (12, 12, player_health, 20))

    # Render the text for the health value
    player_health_font = pygame.font.Font(None, 36)  # You can adjust the font size as needed
    if player_health <= 0:
        player_health_text = player_health_font.render("0", True, WHITE)
    else:
        player_health_text = player_health_font.render(str(player_health), True, WHITE)

    # Blit the health text next to the health bar
    screen.blit(player_health_text, (120, 15))  # Position the text just to the right of the health bar

# Draw game over screen
def draw_game_over_screen():
    game_over_font = pygame.font.Font(None, 72)
    game_over_text = game_over_font.render("Game Over", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

# Main game loop
paused = False
running = True
on_second_level = False  # Track if we are on the second level

while running:
    clock.tick(FPS)
    screen.fill(WHITE)
    screen.blit(background_image, (0, 0))
    print(player_pos)
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

    # Switch to second level when player reaches Y > 650
    if player_pos[1] > 650 and not on_second_level and player_pos[0]> 190 and player_pos[0] < 250:
        on_second_level = True
        platforms = second_level_platforms  # Switch to the second level platforms
        handle_second_level()  # Set up enemies and spikes for the second level
        player_pos[0] = 100
        player_pos[1] = 0

    # Game logic here
    if paused:
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
    if on_second_level:
        draw_second_level()  # Draw second-level platforms and spikes
    else:
        draw_platforms()  # Draw first-level platforms
    draw_spike_platforms()
    draw_fake_spike_platforms()
    draw_enemies()
    draw_health_bar()

    # Draw player image
    if player_facing_right:
        screen.blit(player_image, player_pos)
    else:
        flipped_image = pygame.transform.flip(player_image, True, False)
        screen.blit(flipped_image, player_pos)

    # Display slash visual feedback
    if is_slashing:
        slash_rect = pygame.Rect(player_pos[0] - 10, player_pos[1], player_size[0] + 20, player_size[1])
        pygame.draw.rect(screen, (200, 200, 255), slash_rect, 3)

    pygame.display.flip()
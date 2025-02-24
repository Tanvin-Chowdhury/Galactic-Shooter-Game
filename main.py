import pygame
import random
import os
import math


# Game settings
WIDTH = 400
HEIGHT = 600
FPS = 60

# Colors
RED = (255, 0, 0)
GREEN = (100, 200, 50)
ORANGE = (255, 150, 0)
#ORANGE = (252, 182, 29)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
BLACK = (0, 0, 0)

# Initialize pygame
pygame.init()

# Initialize music
pygame.mixer.init()

# Set screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Shooter")
clock = pygame.time.Clock()

# Font
fontName = pygame.font.match_font("times")

# Text function for displaying game text
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(fontName, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# File to store highest score for Easy mode
HIGHEST_SCORE_EASY_FILE = "highest_score_easy.txt"
# File to store highest score for Hard mode
HIGHEST_SCORE_HARD_FILE = "highest_score_hard.txt"

def load_highest_score(mode):
    if mode == "Easy":
        score_file = HIGHEST_SCORE_EASY_FILE
    elif mode == "Hard":
        score_file = HIGHEST_SCORE_HARD_FILE
    else:
        score_file = HIGHEST_SCORE_EASY_FILE  # Default to Easy if invalid mode

    if os.path.exists(score_file):
        with open(score_file, "r") as file:
            try:
                return int(file.read())
            except ValueError:
                return 0  # Return 0 if the file is empty or invalid
    return 0  # Return 0 if the file does not exist

def save_highest_score(score, mode):
    if mode == "Easy":
        score_file = HIGHEST_SCORE_EASY_FILE
    elif mode == "Hard":
        score_file = HIGHEST_SCORE_HARD_FILE
    else:
        score_file = HIGHEST_SCORE_EASY_FILE  # Default to Easy if invalid mode

    with open(score_file, "w") as file:
        file.write(str(score))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("spacePlayer.png"), (50, 50))
        self.rect = self.image.get_rect()
        self.radius = 18
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.lives = 10

    def update(self):
        self.speedx = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speedx = -5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speedx = 5
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self, all_sprites, bullets):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(random.choice(["laserBlue.png", "laserGreen.png"])), (10, 30))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, player=None):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("laserRed.png"), (10, 25))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Calculate the direction towards the player
        dx = player.rect.centerx - x
        dy = player.rect.centery - y
        angle = math.atan2(dy, dx)  # Get angle in radians

        # Set bullet speed
        self.speed = 2
        self.speedx = self.speed * math.cos(angle)  # Calculate x movement
        self.speedy = self.speed * math.sin(angle)  # Calculate y movement

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Remove bullet if it goes off-screen
        if self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, easy_mode=True, all_sprites=None, enemy_bullets=None):
        pygame.sprite.Sprite.__init__(self)
        self.image_org = pygame.transform.scale(pygame.image.load(random.choice(
            ["enemy1.png", "enemy2.png", "enemy3.png", "enemy4.png", "enemy5.png", "enemy6.png", "enemy7.png",
             "enemy8.png", "enemy9.png"])), (30,30))
        self.image = pygame.transform.scale(self.image_org, (30, 30))
        self.rect = self.image.get_rect()
        self.radius = 18
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randint(1, 3)
        self.speedx = random.choice([-2, -1, 0, 1, 2])
        self.rot = 0
        self.target = player
        self.rot_speed = random.randrange(-5, 5)
        self.easy_mode = easy_mode
        self.last_shot = pygame.time.get_ticks()
        self.all_sprites = all_sprites
        self.enemy_bullets = enemy_bullets

    def update(self):
        if self.easy_mode:
            # for easy mode: random movement
            self.rect.x += self.speedx
            self.rect.y += self.speedy
            if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
                self.rect.x = random.randrange(WIDTH - self.rect.width)
                self.rect.y = random.randrange(-100, -40)
                self.speedy = random.randrange(1, 8)
                self.speedx = random.randrange(-3, 3)

        else:
            # for hard mode: using AI
            if self.rect.centerx < self.target.rect.centerx:
                self.rect.x += min(2, self.speedx)
            elif self.rect.centerx > self.target.rect.centerx:
                self.rect.x -= min(2, abs(self.speedx))

            self.rect.y += self.speedy
            if self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
                self.rect.x = random.randint(0, WIDTH - self.rect.width)
                self.rect.y = random.randint(-100, -40)
                self.speedy = random.randint(1, 3)

            # Enemy shooting logic
            now = pygame.time.get_ticks()
            if now - self.last_shot > 2000:  # Fire every 2 second
                self.last_shot = now
                enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, self.target)
                self.all_sprites.add(enemy_bullet)
                self.enemy_bullets.add(enemy_bullet)


# File to store highest score for Easy mode
HIGHEST_SCORE_EASY_FILE = "highest_score_easy.txt"
# File to store highest score for Hard mode
HIGHEST_SCORE_HARD_FILE = "highest_score_hard.txt"

def load_highest_score(mode):
    if mode == "Easy":
        score_file = HIGHEST_SCORE_EASY_FILE
    elif mode == "Hard":
        score_file = HIGHEST_SCORE_HARD_FILE
    else:
        score_file = HIGHEST_SCORE_EASY_FILE  # Default to Easy if invalid mode

    if os.path.exists(score_file):
        with open(score_file, "r") as file:
            try:
                return int(file.read())
            except ValueError:
                return 0  # Return 0 if the file is empty or invalid
    return 0  # Return 0 if the file does not exist

def save_highest_score(score, mode):
    if mode == "Easy":
        score_file = HIGHEST_SCORE_EASY_FILE
    elif mode == "Hard":
        score_file = HIGHEST_SCORE_HARD_FILE
    else:
        score_file = HIGHEST_SCORE_EASY_FILE  # Default to Easy if invalid mode
    with open(score_file, "w") as file:
        file.write(str(score))

#background image
game_background = pygame.image.load("background.jpeg")
game_background_rect = game_background.get_rect()

background = pygame.image.load("background1.jpeg")
background_rect = background.get_rect()

def menu():
    gameOn = True
    while gameOn:
        if pygame.display.get_surface() is not None:
            screen.fill(BLACK)
            screen.blit(background, background_rect)
            draw_text(screen, "GALACTIC SHOOTER", 36, WIDTH // 2, 100)

            easy_button = pygame.Rect(WIDTH // 2 - 50, 250, 100, 40)
            hard_button = pygame.Rect(WIDTH // 2 - 50, 310, 100, 40)
            exit_button = pygame.Rect(WIDTH // 2 - 50, 370, 100, 40)

            # Button colors
            easy_button_color = GREEN
            hard_button_color = RED
            exit_button_color = ORANGE

            # Border color and thickness
            border_color = WHITE
            border_thickness = 2
            border_radius = 5

            # Draw filled button with color
            pygame.draw.rect(screen, easy_button_color, easy_button, border_radius=border_radius)
            pygame.draw.rect(screen, hard_button_color, hard_button, border_radius=border_radius)
            pygame.draw.rect(screen, exit_button_color, exit_button, border_radius=border_radius)

            # Draw button borders with rounded corners
            pygame.draw.rect(screen, border_color, easy_button, border_thickness, border_radius = border_radius)
            pygame.draw.rect(screen, border_color, hard_button, border_thickness, border_radius = border_radius)
            pygame.draw.rect(screen, border_color, exit_button, border_thickness, border_radius = border_radius)

            draw_text(screen, "Easy", 20, WIDTH // 2, 258)
            draw_text(screen, "Hard", 20, WIDTH // 2, 318)
            draw_text(screen, "Exit", 20, WIDTH // 2, 378)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if easy_button.collidepoint(mouse_x, mouse_y):
                        game_loop("Easy")
                    elif hard_button.collidepoint(mouse_x, mouse_y):
                        game_loop("Hard")
                    elif exit_button.collidepoint(mouse_x, mouse_y):
                        pygame.quit()


def game_over_screen(score, mode):
    pygame.time.delay(1000)
    screen.fill(BLACK)
    screen.blit(background, background_rect)

    restart_button = pygame.Rect(WIDTH // 2 - 50, 353, 100, 40)
    exit_button = pygame.Rect(WIDTH // 2 - 50, 423, 100, 40)

    # Button colors
    restart_button_color = GREEN
    exit_button_color = ORANGE


    # Border color and thickness
    border_color = WHITE
    border_thickness = 2
    border_radius = 5

    # Draw filled button with color
    pygame.draw.rect(screen, restart_button_color, restart_button, border_radius=border_radius)
    pygame.draw.rect(screen, exit_button_color, exit_button, border_radius=border_radius)

    # Draw button borders with rounded corners
    pygame.draw.rect(screen, border_color, restart_button, border_thickness, border_radius=border_radius)
    pygame.draw.rect(screen, border_color, exit_button, border_thickness, border_radius=border_radius)

    draw_text(screen, "GAME OVER", 45, WIDTH // 2, 150)
    draw_text(screen, f"Your Score: {score}", 25, WIDTH // 2, 220)
    draw_text(screen, f"Highest Score: {load_highest_score(mode)}", 25, WIDTH // 2, 260)

    draw_text(screen, "Restart", 20, WIDTH // 2, 360)
    draw_text(screen, "Exit", 20, WIDTH // 2, 430)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    game_loop(mode)  # Restart the game
                    waiting = False
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    return

def game_loop(mode):
    global highest_score
    score = 0
    my_player = Player()
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    all_sprites.add(my_player)
    enemy_bullets = pygame.sprite.Group()

    # Load highest score based on selected mode
    highest_score = load_highest_score(mode)

    # Generate enemies
    for i in range(8):
        e = Enemy(my_player, easy_mode=(mode == "Easy"), all_sprites=all_sprites, enemy_bullets=enemy_bullets)
        all_sprites.add(e)
        enemies.add(e)

    game_on = True
    while game_on:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_on = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    my_player.shoot(all_sprites, bullets)

        # Update
        all_sprites.update()
        enemy_bullets.update()

        # Check collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 20 - hit.radius
            e = Enemy(my_player, easy_mode=(mode == "Easy"), all_sprites=all_sprites, enemy_bullets=enemy_bullets)
            all_sprites.add(e)
            enemies.add(e)

        # Check player collisions with enemies
        hits = pygame.sprite.spritecollide(my_player, enemies, False, pygame.sprite.collide_circle)
        if hits:
            game_on = False

        # Check collisions between player and enemy bullets
        if mode == "Hard":
            # difficulty - only bullet collide player
            #hits = pygame.sprite.spritecollide(my_player, enemy_bullets, True)

            # difficulty - both bullet and enemy collide player
            hits = pygame.sprite.spritecollide(my_player, enemy_bullets, True)
            for hit in hits:
                my_player.lives -= 1  # Reduce player's life by 1
                if my_player.lives <= 0:  # End the game if no lives left
                    game_on = False

        # Update the highest score
        if score > highest_score:
            highest_score = score
            save_highest_score(highest_score, mode)

        # Fill screen with black and draw background
        screen.fill(BLACK)
        screen.blit(game_background, game_background_rect)

        # Draw all sprites
        all_sprites.draw(screen)

        # Display score and highest score
        draw_text(screen, f"Current Score: {score}", 18, 325, 10)
        draw_text(screen, f"Highest Score: {highest_score}", 18, 70, 10)
        draw_text(screen, f"Lives: {my_player.lives}", 18, WIDTH // 2, 40)

        pygame.display.flip()

    save_highest_score(highest_score, mode)
    game_over_screen(score, mode)

menu()
pygame.quit()


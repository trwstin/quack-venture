import pygame
import sys
import random

pygame.init()

# Global Variables
SURFACE_COLOR = (255, 255, 255)  # Background color (white)
WIDTH = 800
HEIGHT = 600

# Object class
class Sprite(pygame.sprite.Sprite):
    def __init__(self, image_paths, width, height):
        super().__init__()

        self.images = [pygame.image.load(path) for path in image_paths]
        self.images = [pygame.transform.scale(image, (width, height)) for image in self.images]
        self.frame = 0
        self.image = self.images[self.frame]
        self.rect = self.image.get_rect()
        self.life = 3

    def moveRight(self, pixels):
        self.rect.x += pixels

    def moveLeft(self, pixels):
        self.rect.x -= pixels

    def moveForward(self, pixels):
        self.rect.y += pixels

    def moveBack(self, pixels):
        self.rect.y -= pixels

    def collision_wall(self):
        # Add collision detection with screen edges
        if self.rect.left < 0:
            self.rect.left = 0
            self.moveRight(10)
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.moveLeft(10)

        if self.rect.top < 0:
            self.rect.top = 0
            self.moveForward(10)  # check top logic
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.moveBack(10)

    def moveRandom(self):
        direction = random.choice(['up', 'down', 'left', 'right'])
        speed = 0.5

        if direction == 'up':
            self.moveBack(speed)
        elif direction == 'down':
            self.moveForward(speed)
        elif direction == 'left':
            self.moveLeft(speed)
        else:
            self.moveRight(speed)

    def update(self):
        self.frame = (self.frame + 1) % len(self.images)
        self.image = self.images[self.frame]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, dest_x, dest_y):
        super().__init__()

        self.image = pygame.image.load('bullet.png')
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

        self.speed = 7
        self.start_x = start_x
        self.start_y = start_y
        self.dest_x = dest_x
        self.dest_y = dest_y

    def update(self):
        dx = self.dest_x - self.start_x
        dy = self.dest_y - self.start_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > 0:
            self.rect.x += self.speed * dx / distance
            self.rect.y += self.speed * dy / distance

pygame.init()

size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("QNA")

all_sprites_list = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()

background_image = pygame.image.load("map.png")
background_rect = background_image.get_rect()

# Use a list of image paths for animated sprites
player = Sprite([f"player/tile{i:03d}.png" for i in range(12)], 30, 30)
player.rect.x = 200
player.rect.y = 300
player.life = 3  # Initialize main character's life

all_sprites_list.add(player)

game_state = "running"  # "running", "paused", or "over"
exit_game = False
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)  # Font for displaying text

# Function to respawn zombies
def respawn_zombie():
    zombie = Sprite([f"enemies/tile{i:03d}.png" for i in range(12)], 30, 30)
    zombie.rect.x = random.randint(50, WIDTH - 50)
    zombie.rect.y = random.randint(50, HEIGHT - 50)
    all_sprites_list.add(zombie)
    zombie_group.add(zombie)

# Initial zombie respawn
for _ in range(5):  # Spawn 5 zombies initially
    respawn_zombie()

bullet_list = pygame.sprite.Group()

zombie_kills = 0
while not exit_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                exit_game = True
            elif event.key == pygame.K_SPACE and game_state == "running":

                # Shoot a bullet towards a random zombie
                if len(zombie_group) > 0:
                    target_zombie = random.choice(zombie_group.sprites())
                    bullet = Bullet(player.rect.x, player.rect.y, target_zombie.rect.x, target_zombie.rect.y)
                    bullet_list.add(bullet)
                    all_sprites_list.add(bullet)
            elif event.key == pygame.K_ESCAPE:
                if game_state == "running":
                    game_state = "paused"
                elif game_state == "paused":
                    game_state = "running"

    keys = pygame.key.get_pressed()
    if game_state == "running":
        if keys[pygame.K_LEFT]:
            player.moveLeft(10)
        if keys[pygame.K_RIGHT]:
            player.moveRight(10)
        if keys[pygame.K_DOWN]:
            player.moveForward(10)
        if keys[pygame.K_UP]:
            player.moveBack(10)
        player.collision_wall()

    # Update bullets
    bullet_list.update()

    # Check for collision between bullets and zombies
    collisions = pygame.sprite.groupcollide(zombie_group, bullet_list, False, True)
    

    for zombie in collisions.keys():
        print("Zombie hit by bullet!")
        zombie.life -= 1
        if zombie.life <= 0:
            zombie.kill()  # Remove the zombie if life is 0
            zombie_kills += 1
            respawn_zombie()  # Respawn a new zombie

    # Check for collision between player and zombies
    if pygame.sprite.spritecollide(player, zombie_group, False):
        print("Player collided with Zombie!")
        player.life -= 1  # Decrease player's life
        if player.life <= 0:
            game_state = "over"

    all_sprites_list.update()

    screen.fill(SURFACE_COLOR)
    
    screen.blit(background_image, background_rect)
    all_sprites_list.draw(screen)

    # Display main character's remaining life
    player_life_text = font.render(f'Player Life: {max(0, player.life)}', True, (255, 0, 0))
    screen.blit(player_life_text, (10, 10))

    # Display zombie kill count
    zombie_life_text = font.render(f'Zombie Killed: { zombie_kills }', True, (255, 0, 0))
    screen.blit(zombie_life_text, (10, 30))

    if game_state == "paused":
        # Display pause menu
        pause_text = font.render("Game Paused, Press Esc to Continue", True, (0, 0, 0))
        screen.blit(pause_text, ((WIDTH - pause_text.get_width()) // 2, (HEIGHT - pause_text.get_height()) // 2))

    pygame.display.flip()
    clock.tick(30)  # Adjusted frame rate for smoother motion

    if game_state == "over":
        pygame.time.delay(2000)  # Delay for 2000 milliseconds (2 seconds)
        exit_game = True

pygame.quit()
sys.exit()
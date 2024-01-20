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
    def __init__(self, color, width, height, start_x, start_y, dest_x, dest_y):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(color)
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

background_image = pygame.image.load("map.png")
background_rect = background_image.get_rect()

# Use a list of image paths for animated sprites
player = Sprite([f"player/tile{i:03d}.png" for i in range(12)], 30, 30)
player.rect.x = 200
player.rect.y = 300
player.life = 3  # Initialize main character's life

zombie = Sprite([f"enemies/tile{i:03d}.png" for i in range(12)], 30, 30)
zombie.rect.x = 100
zombie.rect.y = 100
zombie.life = 3  # Initialize zombie's life

bullet_list = pygame.sprite.Group()

all_sprites_list.add(player, zombie)

game_state = "running"  # "running" or "over"
exit_game = False
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)  # Font for displaying text

while not exit_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                exit_game = True
            elif event.key == pygame.K_SPACE and game_state == "running":
                # Shoot a bullet towards the zombie
                bullet = Bullet((0, 0, 255), 5, 5, player.rect.x, player.rect.y, zombie.rect.x, zombie.rect.y)
                bullet_list.add(bullet)
                all_sprites_list.add(bullet)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.moveLeft(10)
    if keys[pygame.K_RIGHT]:
        player.moveRight(10)
    if keys[pygame.K_DOWN]:
        player.moveForward(10)
    if keys[pygame.K_UP]:
        player.moveBack(10)

    player.collision_wall()

    zombie.moveRandom()
    zombie.collision_wall()

    # Update bullets
    bullet_list.update()

    # Check for collision between bullet and zombie
    if pygame.sprite.spritecollide(zombie, bullet_list, True):
        print("Zombie hit by bullet!")
        zombie.life -= 1  # Decrease zombie's life
        if zombie.life <= 0:
            game_state = "over"

    # Check for collision between player and zombie
    if pygame.sprite.collide_rect(player, zombie):
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

    # Display zombie's remaining life
    zombie_life_text = font.render(f'Zombie Life: {max(0, zombie.life)}', True, (0, 255, 0))
    screen.blit(zombie_life_text, (10, 50))

    pygame.display.flip()
    clock.tick(30)  # Adjusted frame rate for smoother motion

    if game_state == "over":
        pygame.time.delay(2000)  # Delay for 2000 milliseconds (2 seconds)
        exit_game = True

pygame.quit()
sys.exit()

import sys
import random
import pygame
import pygame_menu
import pygamepopup

from pygamepopup.components import Button, InfoBox, TextElement
from pygamepopup.menu_manager import MenuManager
from quiz_data import *

pygame.init()
pygamepopup.init()

pygame.mixer.init()
pygame.mixer.music.load('assets/music/bgm.ogg')
pygame.mixer.music.play(-1)
pygame.display.set_caption("Quackers Adventure")

SURFACE_COLOR = (255, 255, 255)
WIDTH = 800
HEIGHT = 600

size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

background_image = pygame.image.load("assets/bg/map.png")
background_rect = background_image.get_rect()

all_sprites_list = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()

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
    
    def addLife(self):
        self.life += 1

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

    def moveRandom(self, target_x, target_y):
        direction = random.choice(['up', 'down', 'left', 'right'])
        speed = 10

        if direction == 'up' and self.rect.y > target_y:
            self.moveBack(speed)
        elif direction == 'down' and self.rect.y < target_y:
            self.moveForward(speed)
        elif direction == 'left' and self.rect.x > target_x:
            self.moveLeft(speed)
        elif direction == 'right' and self.rect.x < target_x:
            self.moveRight(speed)

    def update(self):
        self.frame = (self.frame + 1) % len(self.images)
        self.image = self.images[self.frame]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, dest_x, dest_y):
        super().__init__()

        self.image = pygame.image.load('assets/sprites/bullet.png')
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

# Load player sprites
player = Sprite([f"assets/sprites/player/tile{i:03d}.png" for i in range(12)], 30, 30)
player.rect.x = 200
player.rect.y = 300
player.life = 3  # Initialize main character's life

all_sprites_list.add(player)

menu_manager = MenuManager(screen)

INSIGHT_MENU_ID = "insight"
def insight_menu(item):
    insight_menu = InfoBox(
        "INSIGHT",
        [
            [
                TextElement(
                    text=item
                )
            ]
        ],
        width=500,
        identifier=INSIGHT_MENU_ID,
        close_button_text='Continue (Q)'
    )
    return insight_menu

QUIZ_MENU_ID = "quiz"
def quiz_menu(dict, player):
    quiz_menu = InfoBox(
        dict.get('question'),
        [
            [
                Button(
                        title=dict.get('answer'),
                        callback=lambda: player.addLife(),
                        # Correct Menu Popup
                )
            ],
            [
                Button(
                        title=dict.get('fake1'),
                        callback=lambda: respawn_zombie(),
                )
            ],
            [
                Button(
                        title=dict.get('fake2'),
                        callback=lambda: respawn_zombie(),
                )
            ],
            [
                Button(
                        title=dict.get('fake3'),
                        callback=lambda: respawn_zombie(),
                )
            ],
        ],
        width=800,
        identifier=INSIGHT_MENU_ID,
        has_close_button=False
    )
    return quiz_menu

# For insights
def txt_to_list(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
    return lines

# Function for sound effects
def sound_effect(sound_file):
    pygame.mixer.init()
    pygame.mixer.Sound(sound_file)
    pygame.mixer.Sound(sound_file).play()

# Function to respawn zombies
def respawn_zombie():
    enemy = random.randint(0, 2)
    zombie = Sprite(["assets/sprites/enemies/{:d}/".format(enemy) + f"tile{i:03d}.png" for i in range(12)], 34, 30)
    
    # Ensure the zombie spawns a decent distance away from the player
    min_distance = 200
    while True:
        zombie.rect.x = random.randint(100, WIDTH - 50)
        zombie.rect.y = random.randint(100, HEIGHT - 50)
        
        # Calculate the distance between the zombie and the player
        distance = ((zombie.rect.x - player.rect.x) ** 2 + (zombie.rect.y - player.rect.y) ** 2) ** 0.5
        
        if distance >= min_distance:
            break

    all_sprites_list.add(zombie)
    zombie_group.add(zombie)

# Function for game over screen
def game_over_screen():
    game_over_text = font.render("QUACKERS HAS DIED", True, (255, 0, 0))
    screen.blit(game_over_text, ((WIDTH - game_over_text.get_width()) // 2, (HEIGHT - game_over_text.get_height()) // 2))

def congratulations_screen():
    rainbow_colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (128, 0, 128)]

    # Fill the screen with a rainbow pattern
    for i, color in enumerate(rainbow_colors):
        rect = pygame.Rect(0, i * (HEIGHT // len(rainbow_colors)), WIDTH, HEIGHT // len(rainbow_colors))
        pygame.draw.rect(screen, color, rect)

    # Display the congratulations text on top
    congrats_text = font.render("Congratulations! Quackers is now financially literate :)", True, (0, 0, 0))
    screen.blit(congrats_text, ((WIDTH - congrats_text.get_width()) // 2, (HEIGHT - congrats_text.get_height()) // 2))


# Display a menu
def show_menu(menu):
    if menu_manager.active_menu is not None:
        if menu_manager.active_menu.identifier == menu.identifier:
            return
        else:
            menu_manager.close_active_menu()
    menu_manager.open_menu(menu)

def start():
    # Initial zombie respawn
    NUM_ZOMBIES = 7
    for _ in range(NUM_ZOMBIES): # Spawn 5 zombies initially
        respawn_zombie()

    bullet_list = pygame.sprite.Group()

    zombie_kills = 0
    game_state = "running" # "running", "paused", or "over"
    exit_game = False
    menu_open = False
    insights = txt_to_list('assets/insights.txt')
    quiz_count = 1

    # Game Loop
    while not exit_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    exit_game = True
                elif event.key == pygame.K_SPACE and game_state == "running":
                    if len(zombie_group) > 0:
                        sound_effect('assets/music/quack.mp3')
                        target_zombie = random.choice(zombie_group.sprites())
                        bullet = Bullet(player.rect.x, player.rect.y, target_zombie.rect.x, target_zombie.rect.y)
                        bullet_list.add(bullet)
                        all_sprites_list.add(bullet)
                elif event.key == pygame.K_ESCAPE:
                    if game_state == "running":
                        game_state = "paused"
                    elif game_state == "paused":
                        game_state = "running"
                elif menu_open and event.key == pygame.K_q and menu_manager.active_menu.identifier == INSIGHT_MENU_ID:
                    game_state = "running"
                    menu_open = False
                    menu_manager.close_active_menu()
            elif event.type == pygame.MOUSEMOTION:
                menu_manager.motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 or event.button == 3:
                    game_state = "running"
                    menu_manager.click(event.button, event.pos)
                    menu_manager.close_active_menu()

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

            # Update zombies
            for zombie in zombie_group:
                zombie.moveRandom(player.rect.x, player.rect.y)
                zombie.collision_wall()

        # Update bullets
        bullet_list.update()

        # Check for collision between bullets and zombies
        collisions = pygame.sprite.groupcollide(zombie_group, bullet_list, False, True)

        for zombie in collisions.keys():
            zombie.life -= 1
            if zombie.life <= 0:
                zombie.kill()  # Remove the zombie if life is 0
                zombie_kills += 1
                respawn_zombie()  # Respawn a new zombie

        # Check for collision between player and zombies
        collided_zombies = pygame.sprite.spritecollide(player, zombie_group, False)
        for zombie in collided_zombies:
            player.life -= 1  # Decrease player's life
            if player.life <= 0:
                game_state = "over"
            else:
                # If player is still alive, instantly kill the zombie
                zombie.life = 0
                zombie.kill()
                zombie_kills += 1
                respawn_zombie()  # Respawn a new zombie

        all_sprites_list.update()

        screen.fill(SURFACE_COLOR)

        screen.blit(background_image, background_rect)
        all_sprites_list.draw(screen)

        # Display main character's remaining life
        player_life_text = font.render(f'Quackers HP: {max(0, player.life)}', True, (0, 255, 0))
        screen.blit(player_life_text, (10, 10))

        # Display zombie kill count
        zombie_life_text = font.render(f'Zombies Killed: {zombie_kills}', True, (255, 0, 0))
        screen.blit(zombie_life_text, (10, 40))

        # Controls
        controls_1 = font.render('Arrow Keys: Move', True, (0, 0, 255))
        screen.blit(controls_1, (580, 10))
        controls_2 = font.render('Spacebar: Quack', True, (0, 0, 255))
        screen.blit(controls_2, (580, 40))
        controls_3 = font.render('Esc/Q: Pause', True, (0, 0, 255))
        screen.blit(controls_3, (580, 70))

        if menu_open and menu_manager.active_menu is not None:
            if menu_manager.active_menu.identifier == INSIGHT_MENU_ID or menu_manager.active_menu.identifier == QUIZ_MENU_ID:
                game_state = "paused"
            else:
                game_state = "running"

        if game_state == "paused":
            # Display pause menu
            pause_text = font.render("Game Paused, Press Esc to Continue", True, (0, 0, 0))
            screen.blit(pause_text, ((WIDTH - pause_text.get_width()) // 2, (HEIGHT - pause_text.get_height()) // 2))

        if game_state == "over":
            game_over_screen()
            pygame.display.flip()
            clock.tick(0)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    exit_game = True
        
        if zombie_kills > 0 and zombie_kills % 9 == 0:
            menu_open = True
            show_menu(insight_menu(insights.pop()))
            zombie_kills += 1
        
        if zombie_kills > 0 and zombie_kills % 15 == 0:
            menu_open = True
            show_menu(quiz_menu(quiz_data.get(quiz_count),player))
            quiz_count += 1
            zombie_kills += 1
        
        if quiz_count == 10 and menu_manager.active_menu is None:
            zombie_kills = 0
            congratulations_screen()
            pygame.display.flip()
            clock.tick(0)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    exit_game = True

        pygame.display.flip()
        menu_manager.display()
        pygame.display.update()
        clock.tick(30)            

# Design for menu screen
my_theme = pygame_menu.themes.THEME_ORANGE.copy()
my_theme.widget_font = pygame_menu.font.FONT_8BIT

myimage = pygame_menu.baseimage.BaseImage(
    image_path='assets/bg/menu.png',
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY)

my_theme.background_color = myimage
my_theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE

menu = pygame_menu.Menu('', 800, 600,
                       theme=my_theme)

menu.add.label('Quackers\nAdventure\n')
menu.add.button('Play', start)
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.mainloop(screen)

pygame.quit()
sys.exit()
# /// script
# dependencies = [
#   "pygame-ce"
# ]
# ///

import sys, asyncio
import os
if sys.platform == "emscripten":
    import asyncio
    import platform
    platform.window.canvas.style.imageRendering = "pixelated"
    ASSET_PATH = "assets"
else:
    ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")
import pygame
import time
import random
pygame.font.init()
pygame.init()


WIDTH, HEIGHT = 700, 550
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join(ASSET_PATH, "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join(ASSET_PATH, "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join(ASSET_PATH, "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_PATH, "pixel_ship_yellow.png")), (50, 50))

# Lasers
LASER_W, LASER_H = 60, 75
RED_LASER = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_PATH, "pixel_laser_red.png")), (LASER_W, LASER_H))
GREEN_LASER = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_PATH, "pixel_laser_green.png")), (LASER_W, LASER_H))
BLUE_LASER = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_PATH, "pixel_laser_blue.png")), (LASER_W, LASER_H))
YELLOW_LASER = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_PATH, "pixel_laser_yellow.png")), (LASER_W, LASER_H))


# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_PATH, "background-black.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self. y >= 0)
    
    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_imag = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown( )
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 5, self.y, self.laser_imag)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
        

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_imag = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown( )
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10,
                                             self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10,
                                             self.ship_img.get_width() * (self.health / self.max_health), 10))                                     
            

class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_imag = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_imag)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,  (offset_x, offset_y)) != None

async def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    max_level = 5
    victory = False

    main_font = pygame.font.SysFont("impact", 25)
    lost_font = pygame.font.SysFont("impact", 50)
    victory_font = pygame.font.SysFont("impact", 60)
    


    enemies = []
    wave_length = 0
    enemy_vel = 1

    player_vel = 5
    laser_vel = 6

    player = Player(300, 400)

    clock = pygame.time.Clock()

    lost = False
    victory = False
    victory_count = 0
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # Draw text
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))

        WIN.blit(lives_label, (15, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 15, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost !!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 250))
        elif victory:
            victory_label = victory_font.render("Victory !!", 1, (255, 255, 255))
            WIN.blit(victory_label, (WIDTH/2 - victory_label.get_width()/2, 250))

        pygame.display.update()


    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if victory:
            victory_count += 1
            if victory_count > FPS * 3:
                run = False
            continue

        if len(enemies) == 0:
            if level >= max_level:
                victory = True
                lost = False
            else:
                level += 1
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame. K_LEFT] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: #up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20 < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers (laser_vel,player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
                
        player.move_lasers(-laser_vel, enemies)

        await asyncio.sleep(0)

async def main_menu():
    title_font = pygame.font.SysFont("impact", 45)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 250))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                await main()
        await asyncio.sleep(0)


asyncio.run(main_menu())
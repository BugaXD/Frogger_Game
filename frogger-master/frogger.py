#! /usr/bin/env python
import pygame
import random as Random
from pygame.locals import *
from sys import exit

pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100, 32, 2, 4096)

# --- Fonts ---
font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 72)
info_font = pygame.font.SysFont(font_name, 24)
menu_font = pygame.font.SysFont(font_name, 36)

# --- Screen setup ---
screen = pygame.display.set_mode((448, 546), 0, 32)
pygame.display.set_caption('frog stack')
clock = pygame.time.Clock()

# --- Load images ---
background_filename = './images/bg.png'
frog_filename = './images/sprite_sheets_up.png'
arrived_filename = './images/frog_arrived.png'
car1_filename = './images/car1.png'
car2_filename = './images/car2.png'
car3_filename = './images/car3.png'
car4_filename = './images/car4.png'
car5_filename = './images/car5.png'
plataform_filename = './images/tronco.png'

background = pygame.image.load(background_filename).convert()
sprite_sapo = pygame.image.load(frog_filename).convert_alpha()
sprite_arrived = pygame.image.load(arrived_filename).convert_alpha()
sprite_car1 = pygame.image.load(car1_filename).convert_alpha()
sprite_car2 = pygame.image.load(car2_filename).convert_alpha()
sprite_car3 = pygame.image.load(car3_filename).convert_alpha()
sprite_car4 = pygame.image.load(car4_filename).convert_alpha()
sprite_car5 = pygame.image.load(car5_filename).convert_alpha()
sprite_plataform = pygame.image.load(plataform_filename).convert_alpha()

# --- Load Sounds ---
hit_sound = pygame.mixer.Sound('./sounds/boom.wav')
agua_sound = pygame.mixer.Sound('./sounds/agua.wav')
chegou_sound = pygame.mixer.Sound('./sounds/success.wav')
trilha_sound = pygame.mixer.Sound('./sounds/guimo.wav')

# --- Classes ---
class Object():
    def __init__(self, position, sprite):
        self.sprite = sprite
        self.position = position

    def draw(self, camera_offset=0):
        screen.blit(self.sprite, (self.position[0], self.position[1] + camera_offset))

    def rect(self):
        return Rect(self.position[0], self.position[1],
                    self.sprite.get_width(), self.sprite.get_height())


class Frog(Object):
    def __init__(self, position, sprite_sapo):
        super().__init__(position, sprite_sapo)
        self.lives = 3
        self.animation_counter = 0
        self.animation_tick = 1
        self.way = "up"
        self.can_move = 1
        self.score = 0
        self.highest_position = position[1]
        self.stack_count = 0  # FOR STACK ATTRIBUTE

    def updateSprite(self, direction):
        if self.way != direction:
            self.way = direction
            if self.way == "up":
                self.sprite = pygame.image.load('./images/sprite_sheets_up.png').convert_alpha()
            elif self.way == "down":
                self.sprite = pygame.image.load('./images/sprite_sheets_down.png').convert_alpha()
            elif self.way == "left":
                self.sprite = pygame.image.load('./images/sprite_sheets_left.png').convert_alpha()
            elif self.way == "right":
                self.sprite = pygame.image.load('./images/sprite_sheets_right.png').convert_alpha()

    def moveFrog(self, key_pressed, key_up):
        if self.animation_counter == 0:
            self.updateSprite(key_pressed)
        self.incAnimationCounter()

        if key_up == 1:
            if key_pressed == "up":
                self.position[1] -= 13
                if self.position[1] < self.highest_position:
                    self.highest_position = self.position[1]
                    self.score += 1
            elif key_pressed == "down":
                if self.position[1] < 475:
                    self.position[1] += 13
            elif key_pressed == "left":
                self.position[0] -= 13
            elif key_pressed == "right":
                self.position[0] += 13

    def animateFrog(self, key_pressed, key_up):
        if self.animation_counter != 0:
            if self.animation_tick <= 0:
                self.moveFrog(key_pressed, key_up)
                self.animation_tick = 1
            else:
                self.animation_tick -= 1

    def setPositionToInitialPosition(self):
        self.position = [207, 475]
        self.highest_position = self.position[1]

    def decLives(self):
        self.lives -= 1

    def cannotMove(self):
        self.can_move = 0

    def incAnimationCounter(self):
        self.animation_counter += 1
        if self.animation_counter == 3:
            self.animation_counter = 0
            self.can_move = 1

    def frogDead(self, game):
        self.setPositionToInitialPosition()
        self.decLives()
        if frog.stack_count > 0:  # STACK 3
            frog.stack_count -= 1
        game.resetTime()
        self.animation_counter = 0
        self.animation_tick = 1
        self.way = "up"
        self.can_move = 1

    def draw(self, camera_offset=0):
        current_sprite = self.animation_counter * 30
        screen.blit(self.sprite, (self.position[0], self.position[1] + camera_offset),
                    (0 + current_sprite, 0, 30, 30 + current_sprite))
        for i in range(self.stack_count):  # STACKING ON TOP OF MAIN FROG FOR EVERY STOP
            y_offset = self.position[1] - (i + 1) * 12
            screen.blit(self.sprite, (self.position[0], y_offset + camera_offset),
                        (0 + current_sprite, 0, 30, 30 + current_sprite))

    def rect(self):
        return Rect(self.position[0], self.position[1], 30, 30)


class Enemy(Object):
    def __init__(self, position, sprite_enemy, way, factor):
        super().__init__(position, sprite_enemy)
        self.way = way
        self.factor = factor

    def move(self, speed):
        if self.way == "right":
            self.position[0] += speed * self.factor
        elif self.way == "left":
            self.position[0] -= speed * self.factor


class Plataform(Object):
    def __init__(self, position, sprite_plataform, way):
        super().__init__(position, sprite_plataform)
        self.way = way

    def move(self, speed):
        if self.way == "right":
            self.position[0] += speed
        elif self.way == "left":
            self.position[0] -= speed


class Game():
    def __init__(self, speed, level):
        self.speed = speed
        self.level = level
        self.points = 0
        self.time = 30
        self.distance = 0

    def incLevel(self):
        self.level += 1

    def incSpeed(self):
        self.speed += 1

    def incPoints(self, points):
        self.points += points

    def decTime(self):
        self.time -= 1

    def resetTime(self):
        self.time = 30


# --- Utility Functions ---
def drawList(objects, camera_offset=0):
    for obj in objects:
        obj.draw(camera_offset)


def moveList(objects, speed):
    for obj in objects:
        obj.move(speed)


def destroyOffscreen(objects):
    for obj in objects[:]:
        if obj.position[0] < -100 or obj.position[0] > 500:
            objects.remove(obj)


def createEnemys(timers, enemys, game):
    for i, tick in enumerate(timers):
        timers[i] -= 1
        if tick <= 0:
            if i == 0:
                timers[0] = (40 * game.speed) / game.level
                enemys.append(Enemy([-55, 436], sprite_car1, "right", 1))
            elif i == 1:
                timers[1] = (30 * game.speed) / game.level
                enemys.append(Enemy([506, 397], sprite_car2, "left", 2))
            elif i == 2:
                timers[2] = (40 * game.speed) / game.level
                enemys.append(Enemy([-80, 357], sprite_car3, "right", 2))
            elif i == 3:
                timers[3] = (30 * game.speed) / game.level
                enemys.append(Enemy([516, 318], sprite_car4, "left", 1))
            elif i == 4:
                timers[4] = (50 * game.speed) / game.level
                enemys.append(Enemy([-56, 280], sprite_car5, "right", 1))


def createPlataforms(timers, plats, game):
    for i, tick in enumerate(timers):
        timers[i] -= 1
        if tick <= 0:
            if i == 0:
                timers[0] = (30 * game.speed) / game.level
                plats.append(Plataform([-100, 200], sprite_plataform, "right"))
            elif i == 1:
                timers[1] = (30 * game.speed) / game.level
                plats.append(Plataform([448, 161], sprite_plataform, "left"))
            elif i == 2:
                timers[2] = (40 * game.speed) / game.level
                plats.append(Plataform([-100, 122], sprite_plataform, "right"))
            elif i == 3:
                timers[3] = (40 * game.speed) / game.level
                plats.append(Plataform([448, 83], sprite_plataform, "left"))
            elif i == 4:
                timers[4] = (20 * game.speed) / game.level
                plats.append(Plataform([-100, 44], sprite_plataform, "right"))


def frogOnTheStreet(frog, enemys, game):
    for e in enemys:
        if frog.rect().colliderect(e.rect()):
            hit_sound.play()
            frog.frogDead(game)


def frogInTheLake(frog, plats, game):
    safe = False
    move_way = None
    for p in plats:
        if frog.rect().colliderect(p.rect()):
            safe = True
            move_way = p.way
    if not safe:
        agua_sound.play()
        frog.frogDead(game)
    else:
        if move_way == "right":
            frog.position[0] += game.speed
        elif move_way == "left":
            frog.position[0] -= game.speed


def whereIsTheFrog(frog, enemys, plats, game):
    if frog.position[1] > 240:
        frogOnTheStreet(frog, enemys, game)
    elif frog.position[1] < 240 and frog.position[1] > 40:
        frogInTheLake(frog, plats, game)


def checkVerticalLoop(frog, game):
    if frog.position[1] < -30:
        frog.position[1] += background.get_height()
        game.incLevel()
        game.incSpeed()
        game.incPoints(50)
        frog.stack_count += 1  # INCREASE STACK COUNT


# --- Main ---
trilha_sound.play(-1)
text_info = menu_font.render('Press any key to start!', 1, (0, 0, 0))
gameInit = 0
camera_y = 0
bg_height = background.get_height()

# --- Start screen ---
while gameInit == 0:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == KEYDOWN:
            gameInit = 1

    bg_y = camera_y % bg_height
    screen.blit(background, (0, bg_y - bg_height))
    screen.blit(background, (0, bg_y))
    screen.blit(text_info, (80, 150))
    pygame.display.update()

# --- Game Loop ---
while True:
    game = Game(3, 1)
    frog = Frog([207, 475], sprite_sapo)
    enemys = []
    plats = []
    ticks_enemys = [30, 0, 30, 0, 60]
    ticks_plats = [0, 0, 30, 30, 30]
    ticks_time = 30
    key_up = 1
    key_pressed = "up"

    while frog.lives > 0:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYUP:
                key_up = 1
            if event.type == KEYDOWN and key_up == 1 and frog.can_move == 1:
                key_pressed = pygame.key.name(event.key)
                frog.moveFrog(key_pressed, key_up)
                frog.cannotMove()

        if not ticks_time:
            ticks_time = 30
            game.decTime()
        else:
            ticks_time -= 1

        if game.time == 0:
            frog.frogDead(game)

        createEnemys(ticks_enemys, enemys, game)
        createPlataforms(ticks_plats, plats, game)
        moveList(enemys, game.speed)
        moveList(plats, game.speed)

        whereIsTheFrog(frog, enemys, plats, game)
        checkVerticalLoop(frog, game)

        # --- Camera follows frog ---
        camera_y = frog.position[1] - 300
        bg_y = camera_y % bg_height

        # --- Draw background loop ---
        screen.blit(background, (0, -bg_y))
        screen.blit(background, (0, -bg_y + bg_height))

        # --- UI ---
        text_info1 = info_font.render(f'Level: {game.level}  Points: {game.points}', 1, (255, 255, 255))
        text_info2 = info_font.render(f'Time: {game.time}   Lifes: {frog.lives}', 1, (255, 255, 255))
        text_info3 = info_font.render(f'Distance: {frog.score}', 1, (255, 255, 255))
        screen.blit(text_info1, (10, 520))
        screen.blit(text_info2, (250, 520))
        screen.blit(text_info3, (10, 500))

        drawList(enemys, -camera_y)
        drawList(plats, -camera_y)

        frog.animateFrog(key_pressed, key_up)
        frog.draw(-camera_y)

        destroyOffscreen(enemys)
        destroyOffscreen(plats)

        pygame.display.update()
        clock.tick(30)

    # --- Game Over ---
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                break
        else:
            screen.blit(background, (0, 0))
            text = game_font.render('GAME OVER', 1, (255, 0, 0))
            text_points = game_font.render(f'Score: {game.points}', 1, (255, 0, 0))
            text_distance = game_font.render(f'Distance: {frog.score}', 1, (255, 0, 0))
            text_reiniciar = info_font.render('Press any key to restart!', 1, (255, 0, 0))
            screen.blit(text, (75, 120))
            screen.blit(text_points, (10, 170))
            screen.blit(text_distance, (10, 220))
            screen.blit(text_reiniciar, (70, 250))
            pygame.display.update()
            continue
        break

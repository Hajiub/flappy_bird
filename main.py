#!/usr/bin/env python3

import pygame as pg
import sys
import random


BIRD_WIDTH = 50
BIRD_HEIGHT = 30
GRAVITY = 0.6
BIRD_STRENGTH = -10
PIPE_WIDTH = 80
PIPE_HIEGHT = 400
SCROLL_SPEED = 4
PIPE_GAP = 150
SCREEN_SIZE = WIDTH, HEIGHT = 400, 700
FPS = 60
GROUND_COLOR = (100, 200, 100)
SKY_COLOR = (173, 216, 230)
PIP_COLOR = (139, 69, 19)
BIRD_COLOR = (255, 255, 0)
PIPE_FREQUENCY = 900


pg.init()
pg.mixer.init()

# game variables
flying = False
game_over = False
score = 0


class Bird(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = BIRD_WIDTH * 3
        self.y = HEIGHT // 2
        self.width, self.height = BIRD_WIDTH, BIRD_HEIGHT
        self.image = pg.Surface((self.width, self.height))
        self.image.fill(BIRD_COLOR)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.vel = 0
        self.bird_strength = BIRD_STRENGTH
        self.got_pressed = False
        self.sound = pg.mixer.Sound("Sounds/wing.wav")

    def update(self):
        if flying:
            self.apply_gravity()

        if not game_over:
            self.jump()

    def apply_gravity(self):
        self.vel += GRAVITY
        if self.vel >= 8:
            self.vel = 8
        self.rect.y += self.vel
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height - 100))

    def jump(self):
        keys = pg.key.get_pressed()
        if pg.mouse.get_pressed()[0] and not self.got_pressed:
            self.vel = self.bird_strength
            self.sound.play()
            self.got_pressed = True

        if not keys[pg.K_SPACE] and not pg.mouse.get_pressed()[0] and self.got_pressed:
            self.got_pressed = False


class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pg.Surface((PIPE_WIDTH, PIPE_HIEGHT))
        self.image.fill(PIP_COLOR)
        self.rect = self.image.get_rect()

        if position == 1:
            self.image = pg.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(PIPE_GAP / 2)]

        elif position == -1:
            self.rect.topleft = [x, y + int(PIPE_GAP / 2)]

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right <= 0:
            self.kill()


class Ground(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((WIDTH, 100))
        self.image.fill(GROUND_COLOR)
        self.rect = self.image.get_rect(topleft=(0, HEIGHT - 100))

def draw_score(win, score, font):
    image = font.render(str(score), True, (255,255,255))
    rect = image.get_rect(center=(WIDTH // 2, 20))
    win.blit(image, rect)

screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("Basic Flappy Bird")
clock = pg.time.Clock()


bird_group = pg.sprite.Group()
bird = Bird()
bird_group.add(bird)

pipe_group = pg.sprite.Group()

ground_group = pg.sprite.Group()
ground = Ground()
ground_group.add(ground)

# The music
hit = pg.mixer.Sound("Sounds/hit.wav")
die = pg.mixer.Sound("Sounds/die.wav")
pt  = pg.mixer.Sound("Sounds/point.wav")


font = pg.font.Font(size=50)
last_pipe = 0
pass_pipe = False

def reset_game():
    pipe_group.empty()
    bird.rect.center = (bird.x, bird.y)
    score = 0
    return score
run = True

while run:

    # handle events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    # fill the screen
    screen.fill(SKY_COLOR)

    # create pipes
    if flying and not game_over:
        current_time = pg.time.get_ticks()
        if current_time - last_pipe >= PIPE_FREQUENCY:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(WIDTH, int(HEIGHT / 2) + pipe_height, -1)
            top_pipe = Pipe(WIDTH, int(HEIGHT / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = current_time

    # Gameover if the bird touches ground
    if bird.rect.bottom >= ground.rect.y and not game_over:
        hit.play()
        flying = False
        game_over = True

    # Game over if the bird touches the pipe or the top of the screen
    elif (
        pg.sprite.groupcollide(bird_group, pipe_group, False, False)
        or bird.rect.top <= 0
    ) and not game_over:
        hit.play()
        die.play()
        game_over = True

    # Score I stole this
    if len(pipe_group) > 0:
        p = pipe_group.sprites()[0]
        if (
            bird.rect.left > p.rect.left
            and bird.rect.right < p.rect.right
            and not pass_pipe and flying
        ):
            pass_pipe = True

        if pass_pipe:
            if bird.rect.left > pipe_group.sprites()[0].rect.right:
                pt.play()
                score += 1
                pass_pipe = False
        
    
    # Update the pipes
    if not game_over and flying:
        pipe_group.update()

    bird_group.update()
    pipe_group.draw(screen)
    ground_group.draw(screen)
    bird_group.draw(screen)

    # Draw the score
    draw_score(screen, score, font)

    if game_over and pg.MOUSEBUTTONDOWN:
        game_over = False
        flying = False
        score = reset_game()
    pg.display.update()
    clock.tick(FPS)

pg.quit()
sys.exit()

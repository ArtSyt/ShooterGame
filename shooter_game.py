#Створи власний Шутер!

from pygame import *
from random import randint
import sys
import os

win_width, win_height = 700, 500
window = display.set_mode((win_width, win_height))
display.set_caption("Sky Military Shooter Simulator 2023 v1.1")

clock = time.Clock()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

ASTERIOD_SPRITE = resource_path("asteroid.png")
BULLET_SPRITE = resource_path("bullet.png")
BACKGROUND_SPRITE = resource_path("galaxy.jpg")
PLAYER_SPRITE = resource_path("rocket.png")
ENEMY_SPRITE = resource_path("ufo.png")

mixer.init()
mixer.music.load(resource_path("space.ogg"))
mixer.music.play()
mixer.music.set_volume(0.125)

fire_sound = mixer.Sound(resource_path("fire.ogg"))

font.init()
main_font = font.SysFont("Arial", 45, True, False)
stats_font = font.SysFont("Arial", 21, True, False)
win_text = main_font.render("Good Job", True, (0, 200, 0))
lose_text = main_font.render("Loser XD", True, (0, 200, 0))

#CLASSES =========================================================

class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__()

        self.image = transform.scale(
            image.load(img), 
            (w, h)
        )

        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    fire_delay = 20 #Задержка между выстрелами
    fire_timer = fire_delay # Таймер
    fire_timer_active = False #Активный таймер (Ограничение стрельбы)
    def update(self):
        #таймер работает когда активен
        #ждем, пока пройдет время таймера
        if self.fire_timer_active:
            #Если  число в таймере > 0, то ждем
            if self.fire_timer > 0:
                self.fire_timer -= 1
            else:
                #Деактивируем и востанавливаем на другой раз
                self.fire_timer_active = False
                self.fire_timer = self.fire_delay
        keys = key.get_pressed()
        if keys[K_a] or keys[K_LEFT]:
            if self.rect.x > 0:
                self.rect.x -= self.speed
        if keys[K_d] or keys[K_RIGHT]:
            if self.rect.x < win_width - self.image.get_width():
                self.rect.x += self.speed
        if keys[K_SPACE]:
            if not self.fire_timer_active:
                self.fire()  #Выстрел
                self.fire_timer_active = True #Активируем таймер

    def fire(self):
        bullet = Bullet(resource_path("bullet.png"), self.rect.centerx, self.rect.y, 30, 40, 5)
        bullet2 = Bullet2(resource_path("bullet.png"), self.rect.x, self.rect.y, 30, 40, 5)
        bullet_group.add(bullet)
        bullet_group.add(bullet2)
        fire_sound.play()

class Enemy(GameSprite):
    def update(self):
        global lost, score
        self.rect.y += self.speed
        if self.rect.y >= win_height or sprite.collide_rect(self, player):
            lost += 1
            self.kill()
        if sprite.spritecollide(self, bullet_group, True):
            score += 1
            self.kill()

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

class Bullet2(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

#CLASSES =========================================================

FPS = 144 # 1 секунда = 144 тиков
GAME_RUN = True
GAME_FINISHED = False

score, lost = 0, 0
spawnrate_delay = FPS * 2
spawnrate_enemy = spawnrate_delay

background = GameSprite(BACKGROUND_SPRITE, 0, 0, win_width, win_height, 0)
player = Player(PLAYER_SPRITE, win_width / 2, win_height - 150, 100, 135, 5)

enemys_group = sprite.Group()
bullet_group = sprite.Group()

# ИГРОВОЙ ЦИКЛ ================================================================

while GAME_RUN:

    for ev in event.get():
        if ev.type == QUIT:
            GAME_RUN = False

    if not GAME_FINISHED:

        score_text = stats_font.render("Вражеских истребителей сбито: " + str(score), True, (7, 33, 14))
        lost_text = stats_font.render("Пропущено истребителей: " + str(lost), True, (7, 33, 14))

        if spawnrate_enemy < 0:
            enemy = Enemy(resource_path("ufo.png"), randint(64, win_width - 64), -64, 64, 64, randint(1, 3))
            enemys_group.add(enemy)
            if spawnrate_delay > FPS * 1:
                spawnrate_delay -= 10
            spawnrate_enemy = spawnrate_delay
        else:
            spawnrate_enemy -= 1    

        background.reset()
        player.reset()
        enemys_group.draw(window)
        bullet_group.draw(window)

        player.update()
        enemys_group.update()
        bullet_group.update()

        window.blit(score_text, (5, 5))
        window.blit(lost_text, (5, score_text.get_height() + 5))

        if score >= 2:
            end_screen = main_font.render("Отличная работа солдат!", True, (150, 9, 9))
            window.blit(end_screen, (win_width / 2 - end_screen.get_width() / 2, win_height / 2 ))
            GAME_FINISHED = True
        if lost >= 3:
            end_screen = main_font.render("Вы не справились с миссией", True, (150, 9, 9))
            window.blit(end_screen, (win_width / 2 - end_screen.get_width() / 2, win_height / 2))
            GAME_FINISHED = True

        display.update()

    clock.tick(FPS)
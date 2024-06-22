#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import csv
import sys
import pygame
import numpy as np

pygame.init()
clock = pygame.time.Clock()
#Width and height of the game
size = w,h = 1000, 600
#Screen, background and player surfaces
screen = pygame.display.set_mode(size)
screen.fill((255,)*3)
background = pygame.image.load('walker_bg.png').convert()

class Soul(pygame.sprite.Sprite):
    def __init__(self, img_path, offset=(0,0)):
        super().__init__()
        self.image = pygame.image.load(img_path).convert_alpha()
        self.pos = self.image.get_rect().move(*offset)
        self.rect = self.pos
        
    #Transform self.pos in a property in order to
    #use float precition in the x and y coordinates.
    @property
    def pos(self):
        x,y,w,h = self._pos
        #Return rounded x and y coordinates Rect.
        return pygame.Rect(round(x), round(y), w, h)
    
    @pos.setter
    def pos(self,o):
        x,y,w,h = o
        #Store as a float list.
        self._pos = [x,y,w,h]

class Walker(Soul):
    DATA_FPS = 60
    Y_POSITION = 30
    
    def __init__(self, data_path, time_offset=0):
        self.data = self.read_data(data_path)
        x = next(iter(self.data.values()))
        super().__init__('walker.png', (x,self.Y_POSITION))
        self.time_offset = time_offset

    def read_data(self, path):
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            data = { int(row['frame']): int(row['x'])
                     for row in reader }
        return data
    
    def update(self):
        millis = pygame.time.get_ticks() - self.time_offset
        frame = millis // (1000 * 1/self.DATA_FPS)
        if frame in self.data:
            #Could use self.pos to use float precition
            self.rect.x = self.data[frame]
            
class Bullet(Soul):
    SPEED = 5
    
    def __init__(self, pos):
        super().__init__('bullet.png', pos)
    
    def update(self):
        self.rect.y -= self.SPEED
        if self.rect.top < 0:
            self.kill()

class Shooter(Soul):
    Y_POSITION = h - 60
    SPEED = 5
    SHOOTING_MILLS = 500
    
    def __init__(self, b_list, all_list, xpos=w/2):
        super().__init__('shooter.png', (xpos, self.Y_POSITION))
        self.b_list = b_list
        self.all_list = all_list
        self.shoot_mills = 0
        self.shooting = False
        
    def update(self):
        keys = pygame.key.get_pressed()
        #2-dimensional vectors
        u = np.ones(2)
        i = u*(1,0)
        # j = u*(0,-1)
        vector = sum([  i*keys[self.k['r']],
                    -i*keys[self.k['l']] ])
                    #     j*keys[self.k['u']],
                    # -j*keys[self.k['d']],
                    # ])
        self.rect.x += (vector*self.SPEED)[0]
        if keys[self.k['s']]:
            now = pygame.time.get_ticks()
            mills = now - self.shoot_mills
            if mills > self.SHOOTING_MILLS:
                self.shooting = False
            if not self.shooting:
                self.shoot()
                self.shoot_mills = now
                self.shooting = True
    
    def shoot(self):
        bullet = Bullet(self.rect.midtop)
        bullet.add(self.b_list, self.all_list)
    
    def set_kbd_dic(self, **kwargs):
        k = { 'r': pygame.K_RIGHT,
              'l': pygame.K_LEFT,
              's': pygame.K_SPACE,
            }
        k.update(kwargs)
        self.k = { key: k[key] for key in 'rls' }

# class Ball(Soul):
#     OFFSET = h/2
#     def __init__(self, x, xspeed, img):
#         surface = pygame.image.load(img)
#         scaled = pygame.transform.scale(surface, (30,30)).convert_alpha()
#         r = scaled.get_rect()
#         pos = [x, h-self.OFFSET-r.h, r.w, r.h]
#         super().__init__(scaled, pos)
#         self.speed = np.array((xspeed,0))
#     
#     def move(self):
#         self._pos[:2] += self.speed

# xspeeds = [3, 1, 4, -1, -3, 2, -2, 1]

walkers = pygame.sprite.Group([Walker('walker_data.csv'), Walker('walker_data_cris.csv')])
bullets = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(walkers)
player = Shooter(bullets, all_sprites)
player.set_kbd_dic()
all_sprites.add(bullets, player)
screen.blit(background,(0,0))

while True:
    #Erase objects using the background
    for o in all_sprites:
        screen.blit(background, o.rect, o.rect)
    #Catch quit event and exit
    for e in pygame.event.get():
        if e.type == pygame.QUIT: sys.exit()
    for o in all_sprites:
        o.update()
    #Chequear colisiones bullets - walkers
    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, walkers, False)
        if hits:
            bullet.kill()
            for walker in hits:
                walker.time_offset = pygame.time.get_ticks()
                walker.add(walkers, all_sprites)
                
        #Paint objects
    all_sprites.draw(screen)
    pygame.display.update()
    #Overall game frames per second
    clock.tick(80)

#if __name__ == '__main__':
#    pass

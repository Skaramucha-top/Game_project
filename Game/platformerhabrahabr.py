#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pygame
from pygame import *
from player import *
from blocks import *


WIN_WIDTH = 1060
WIN_HEIGHT = 720
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#AFEEEE"

pygame.init()

pygame.mixer.music.load('music/C418.mp3')
pygame.mixer.music.play(-1)


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
        
def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l+WIN_WIDTH / 2, -t+WIN_HEIGHT / 2

    l = min(0, l)
    l = max(-(camera.width-WIN_WIDTH), l)
    t = max(-(camera.height-WIN_HEIGHT), t)
    t = min(0, t)

    return Rect(l, t, w, h)        


def main():
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Yandex Liceum Project PyGame")
    bg = Surface((WIN_WIDTH,WIN_HEIGHT))

    bg.fill(Color(BACKGROUND_COLOR))
    
    hero = Player(500, 1700)
    left = right = False
    up = False
    
    entities = pygame.sprite.Group()
    platforms = []
    
    entities.add(hero)
           
    level = [
       "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
       ">                                <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">            --------            <",
       ">                                <",
       ">---                             <",
       ">                              --<",
       ">                                <",
       ">                                <",
       ">                    ---         <",
       ">       --                       <",
       ">                                <",
       ">                                <",
       ">--              --              <",
       ">                                <",
       ">                             -- <",
       ">                                <",
       ">                                <",
       ">   ----                         <",
       ">                                <",
       ">           --                   <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">                      ---       <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">            --------            <",
       ">                                <",
       ">---                             <",
       ">                              --<",
       ">                                <",
       ">                                <",
       ">                    ---         <",
       ">       --                       <",
       ">                                <",
       ">                                <",
       ">--              --              <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">   ----                         <",
       ">                                <",
       ">           --                   <",
       ">                                <",
       ">                      ---       <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">                                <",
       ">--------------------------------<",
       "**********************************"]
       
    timer = pygame.time.Clock()
    x = y = 0
    for row in level:
        for col in row:
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == "*":
                pf = Platform_1(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == ">":
                pf = Platform_2(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == "<":
                pf = Platform_3(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == "^":
                pf = Platform_4(x, y)
                entities.add(pf)
                platforms.append(pf)

            x += PLATFORM_WIDTH
        y += PLATFORM_HEIGHT
        x = 0
    
    total_level_width  = len(level[0])*PLATFORM_WIDTH
    total_level_height = len(level)*PLATFORM_HEIGHT
    
    camera = Camera(camera_configure, total_level_width, total_level_height) 
    
    while 1:
        timer.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT:
                raise SystemExit == QUIT
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True


            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False

        screen.blit(bg, (0, 0))


        camera.update(hero)
        hero.update(left, right, up,platforms)
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        
        
        pygame.display.update()
        

if __name__ == "__main__":
    main()

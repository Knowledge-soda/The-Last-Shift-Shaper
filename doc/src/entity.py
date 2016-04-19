import pygame
from Mind import Orientation, Existence


@Existence.logic_class
class Entity:
    SIZES = {0: 6, 1: 14, 2: 24}
    def __init__(self):
        self.pictures = []
        for x in range(3):
            pic = self.picture[x]
            self.pictures.append([pic, pygame.transform.rotate(pic, 90),
              pygame.transform.rotate(pic, 180),
              pygame.transform.rotate(pic, 270)])
        self.Dir = 0
        self.size = 1
        self.w = self.h = self.SIZES[self.size]
        self.picture = self.pictures[self.size][self.Dir]
        for layer in self.Map.layers:
            if layer.name == "walls":
                self.walls = layer.mapping
        self.obj = Orientation.rect(self.x, self.y, self.w, self.h, self.Map.in_map)
        self.screen = self.Map.screen

    def blit(self):
        self.picture = self.pictures[self.size][self.Dir]

    def move(self):
        tx, mx = divmod(self.x, 10)
        ty, my = divmod(self.y, 10)
        if not self.walls[ty][tx]:
            if mx > my:
                self.x += 10 - mx
            else:
                self.y += 10 - my
        if not self.walls[ty][tx + 1]:
            if mx + self.w > 10:
                if mx + self.w - 10 < 10 - my:
                    self.x -= mx + self.w - 10
                else:
                    self.y += 10 - my
        if not self.walls[ty][tx + 2]:
            if mx + self.w > 20:
                if mx + self.w - 20 < 10 - my:
                    self.x -= mx + self.w - 20
                else:
                    self.y += 10 - my                
        if not self.walls[ty + 1][tx]:
            if my + self.h > 10:
                if my + self.h - 10 < 10 - mx:
                    self.y -= my + self.h - 10
                else:
                    self.x += 10 - mx
        if not self.walls[ty + 1][tx + 1]:
            if mx + self.w > 10 and my + self.h > 10:
                if mx + self.w < my + self.h:
                    self.x -= mx + self.w - 10
                else:
                    self.y -= my + self.h - 10
        if not self.walls[ty + 1][tx + 2]:
            if mx + self.w > 20 and my + self.h > 10:
                if mx + self.w < my + self.h:
                    self.x -= mx + self.w - 20
                else:
                    self.y -= my + self.h - 10
        if not self.walls[ty + 2][tx]:
            if my + self.h > 20:
                if my + self.h - 20 < 10 - mx:
                    self.y -= my + self.h - 10
                else:
                    self.x += 10 - mx
        if not self.walls[ty + 2][tx + 1]:
            if mx + self.w > 10 and my + self.h > 20:
                if mx + self.w < my + self.h:
                    self.x -= mx + self.w - 10
                else:
                    self.y -= my + self.h - 20
        if not self.walls[ty + 2][tx + 2]:
            if mx + self.w > 20 and my + self.h > 20:
                if mx + self.w < my + self.h:
                    self.x -= mx + self.w - 20
                else:
                    self.y -= my + self.h - 20

    def call(self, n):
        if n == 3:
            if self.size:
                self.size -= 1
        elif n == 2:
            if self.size < 2:
                self.size += 1
        self.w = self.h = self.SIZES[self.size]
        self.obj.width = self.obj.height = self.w


@Existence.logic_class
class Player:
    def __init__(self):
        self.keyboard = self.props["keyboard"]
        self.lives = 200

    def blit(self):
        pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(120, 10, self.lives * 2, 20))
        if self.keyboard["up"]:
            self.move(0, -2)
            self.Dir = 0
        if self.keyboard["left"]:
            self.move(-2, 0)
            self.Dir = 1
        if self.keyboard["down"]:
            self.move(0, 2)
            self.Dir = 2
        if self.keyboard["right"]:
            self.move(2, 0)
            self.Dir = 3

    def call(self, n):
        if n == 3:
            if self.size:
                self.size -= 1
        elif n == 2:
            if self.size < 2:
                self.size += 1
        elif n:
            pass
        else:
            self.lives += 20
            self.lives = min(200, self.lives)
        self.w = self.h = self.SIZES[self.size]
        self.obj.width = self.obj.height = self.w

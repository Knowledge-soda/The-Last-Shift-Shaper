import random

import pygame
from Mind import Orientation, Existence

from . import entity, generate


class FakeLayer:
    def __init__(self, x, y, image, screen):
        self.x = x
        self.y = y
        self.image = image
        self.screen = screen
        self.name = ""
        self.sav = 0

    def blit(self):
        self.screen.blit(self.image, (-self.x, -self.y))

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def reset(self):
        self.image.fill((0, 0, 50))

    def save(self):
        pygame.image.save(self.image, str(self.sav) + '.png')
        self.sav += 1


class Arena:
    ROOMS = 20
    MIN_ROOMS = 18
    MAX_ROOMS = 25
    WIDTH = 300
    HEIGHT = 300
    B_BRIDGES = 20
    C_BRIDGES = 20
    MIN_BRIDGES = 15
    MAX_BRIDGES = 30
    def __init__(self, game):
        self.game = game
        self.screen = self.game.screen
        self.keyboard = self.game.keyboard
        self.important = {"game": self.game, "keyboard": self.keyboard}
        pl_pics = [pygame.image.load("doc/art/player/s.png"),
          pygame.image.load("doc/art/player/m.png"),
          pygame.image.load("doc/art/player/b.png")]
        ch_pics = [pygame.image.load("doc/art/chev/s.png"),
          pygame.image.load("doc/art/chev/m.png"),
          pygame.image.load("doc/art/chev/b.png")]
        ent_pics = [pygame.image.load("doc/art/enter/s.png"),
          pygame.image.load("doc/art/enter/m.png"),
          pygame.image.load("doc/art/enter/b.png")]
        tab_pics = [pygame.image.load("doc/art/tab/s.png"),
          pygame.image.load("doc/art/tab/m.png"),
          pygame.image.load("doc/art/tab/b.png")]
        self.Map = Orientation.visual_map(self.WIDTH, self.HEIGHT, path="doc/art",
          decode=[{}, {}, {
          "player": Existence.mov_type(None, pl_pics, props=self.important,
            logic=Existence.Subject + entity.Entity + entity.Player),
          "chev": Existence.mov_type(None, ch_pics, props=self.important,
            logic=entity.Entity),
          "enter": Existence.mov_type(None, ent_pics, props=self.important,
            logic=entity.Entity),
          "tab": Existence.mov_type(None, tab_pics, props=self.important,
            logic=entity.Entity)
          }],
          tilesize=(10, 10), size_in_tiles=True)
        self.Map.create_tileset("map/wall.bmp", "wall")
        self.Map.create_layer("walls")

        self.rooms = []
        self.Map.rooms = self.rooms
        self.bridges = []
        self.bridgesA = []
        self.bridgesB = []
        self.bridgesC = []
        self.fill = 0
        for x in range(self.ROOMS):
            w = random.randint(5, 10)
            h = random.randint(5, 10)
            self.rooms.append(generate.Room(random.randrange(self.WIDTH - w + 1),
              random.randrange(self.HEIGHT - h + 1), w, h, self.Map))
            if x:
                bridge = generate.Bridge(self.rooms[-2], self.rooms[-1], 3, self.Map)
                self.bridges.append(bridge)
                self.bridgesA.append(bridge)
                self.rooms[-2].connect(bridge)
                self.rooms[-1].connect(bridge)
        self.rooms_n = self.ROOMS
        self.A_n = self.ROOMS - 1
        for x in range(self.B_BRIDGES):
            room1 = random.choice(self.rooms)
            room2 = random.choice(self.rooms)
            while room1 == room2:
                room2 = random.choice(self.rooms)
            bridge = generate.Bridge(room1, room2, 2, self.Map)
            self.bridges.append(bridge)
            self.bridgesB.append(bridge)
            room1.connect(bridge)
            room2.connect(bridge)
        self.B_n = self.B_BRIDGES
        for x in range(self.C_BRIDGES):
            room1 = random.choice(self.rooms)
            room2 = random.choice(self.rooms)
            while room1 == room2:
                room2 = random.choice(self.rooms)
            bridge = generate.Bridge(room1, room2, 1, self.Map)
            self.bridges.append(bridge)
            self.bridgesC.append(bridge)
            room1.connect(bridge)
            room2.connect(bridge)
        self.C_n = self.C_BRIDGES

        X, Y = random.choice(list(random.choice(self.rooms).tiles()))
        self.Map.create_objectgroup("live")
        o1 = self.Map.decode[2]["player"](X*10, Y*10, "player", Map=self.Map)
        self.Map.assign_object("live", o1)

        X, Y = random.choice(list(random.choice(self.rooms).tiles()))
        o = self.Map.decode[2]["chev"](X*10, Y*10, "chev", Map=self.Map)
        self.Map.assign_object("live", o)

        X, Y = random.choice(list(random.choice(self.rooms).tiles()))
        o = self.Map.decode[2]["enter"](X*10, Y*10, "enter", Map=self.Map)
        self.Map.assign_object("live", o)

        X, Y = random.choice(list(random.choice(self.rooms).tiles()))
        o = self.Map.decode[2]["tab"](X*10, Y*10, "tab", Map=self.Map)
        self.Map.assign_object("live", o)

        self.up_layer = self.Map.layers[0]
        self.background = pygame.Surface((self.WIDTH * 10, self.HEIGHT * 10))
        self.background.fill((0, 0, 50))
        self.Map.images[0].screen = self.background
        self.up_layer.set_pos(0, 0)
        self.up_layer.get_tiles = self.get_tiles
        self.up_layer.blit()
        self.Map.layers[0] = FakeLayer(0, 0, self.background, self.screen)
        o1.move(0, 0)

        for bridge in self.bridges:
            bridge.check()
        self.rooms[0].set_centre(self)

    def blit(self):
        self.keyboard.update()
        if self.keyboard["flip"] == 1:
            for bridge in self.bridges:
                bridge.fill(self.fill)
            self.fill = not self.fill
        self.Map.blit()
        self.rooms[0].blit()

    def get_tiles(self):
        return (0, 0, self.WIDTH, 0, 0, self.HEIGHT)

    def get_random(self, n):
        if n == 3:
            return (random.choice(self.bridgesC), self.C_n > self.MIN_BRIDGES)
        if n == 2:
            return (random.choice(self.bridgesA), self.A_n > self.MIN_BRIDGES)
        if n:
            return (random.choice(self.bridgesB), self.B_n > self.MIN_BRIDGES)
        return (self.rooms[random.randrange(1, self.rooms_n)], self.rooms_n > self.MIN_ROOMS)

    def new(self, n):
        if n == 3:
            if self.C_n < self.MAX_BRIDGES:
                room1 = random.choice(self.rooms)
                room2 = random.choice(self.rooms)
                while room1 == room2:
                    room2 = random.choice(self.rooms)
                bridge = generate.Bridge(room1, room2, 1, self.Map)
                self.bridges.append(bridge)
                self.bridgesC.append(bridge)
                room1.connect(bridge)
                room2.connect(bridge)
                self.C_n += 1
        elif n == 2:
            if self.A_n < self.MAX_BRIDGES:
                room1 = random.choice(self.rooms)
                room2 = random.choice(self.rooms)
                while room1 == room2:
                    room2 = random.choice(self.rooms)
                bridge = generate.Bridge(room1, room2, 3, self.Map)
                self.bridges.append(bridge)
                self.bridgesA.append(bridge)
                room1.connect(bridge)
                room2.connect(bridge)
                self.A_n += 1                
        elif n:
            if self.B_n < self.MAX_BRIDGES:
                room1 = random.choice(self.rooms)
                room2 = random.choice(self.rooms)
                while room1 == room2:
                    room2 = random.choice(self.rooms)
                bridge = generate.Bridge(room1, room2, 2, self.Map)
                self.bridges.append(bridge)
                self.bridgesB.append(bridge)
                room1.connect(bridge)
                room2.connect(bridge)
                self.B_n += 1                
        elif self.rooms_n < self.MAX_ROOMS and self.A_n < self.MAX_BRIDGES:
            w = random.randint(5, 10)
            h = random.randint(5, 10)
            self.rooms.append(generate.Room(random.randrange(self.WIDTH - w + 1),
              random.randrange(self.HEIGHT - h + 1), w, h, self.Map))
            bridge = generate.Bridge(self.rooms[-2], self.rooms[-1], 3, self.Map)
            self.bridges.append(bridge)
            self.bridgesA.append(bridge)
            self.rooms[-2].connect(bridge)
            self.rooms[-1].connect(bridge)
            self.rooms_n += 1
            self.A_n += 1

    def reduce(self, n):
        if n == 3:
            self.C_n -= 1
        elif n == 2:
            self.A_n -= 1
        elif n:
            self.B_n -= 1
        else:
            self.rooms_n -= 1

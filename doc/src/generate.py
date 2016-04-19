import random

import pygame
from Mind import Orientation


class Room:
    def __init__(self, x, y, w, h, Map):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.Map = Map
        self.Map.write_on(self.tiles(), "walls", 0, "wall", True)
        self.bridges = {1: [], 2: [], 3: []}
        self.obj = Orientation.rect(self.x * 10, self.y * 10, self.w * 10, self.h * 10, self.Map.in_map)
        self.WIDTH = self.Map.t_width
        self.HEIGHT = self.Map.t_height

    def __contains__(self, xy):
        return self.x + self.w > xy[0] >= self.x and self.y + self.h > xy[1] >= self.y

    def __iter__(self):
        return self.tiles()

    def __len__(self):
        return self.w * self.h

    def set_centre(self, arena):
        self.arena = arena
        self.layer = self.arena.up_layer

        self.x_blit = self.x * 10 + self.w * 5 - 20
        self.y_blit = self.y * 10 + self.h * 5 - 20
        self.def_image = pygame.image.load("doc/art/map/centre.png")
        self.image = self.def_image
        self.screen = self.Map.screen

        self.pl = self.Map.clone_obj("player")
        self.pl_obj = self.pl.obj
        self.keyboard = self.pl.keyboard

        self.seq = [0, 0]
        self.pos = 0
        self.images = [pygame.image.load("doc/art/signs/" + str(x) + '.png') for x in range(4)]
        self.state = 0
        self.time = pygame.time.get_ticks()

        self.pos1 = (10, 10)
        self.pos2 = (60, 10)
        self.select = pygame.image.load("doc/art/signs/select.png")

    def update(self):
        Map.write_on(self.tiles, "walls", 0, "wall", True)        

    def blit(self):
        self.screen.blit(self.image, (self.x_blit - self.Map.x, self.y_blit - self.Map.y))
        self.screen.blit(self.images[self.seq[0]], self.pos1)
        self.screen.blit(self.images[self.seq[1]], self.pos2)
        if self.state < 2:
            self.screen.blit(self.select, self.pos2 if self.state else self.pos1)
        if any(self.obj.collide(self.pl_obj)):
            if self.state < 2:
                self.image = self.images[self.pos]
                if self.keyboard["shift"] == 1:
                    self.pos += 1
                    self.pos %= 4
            else:
                self.image = self.def_image
        else:
            self.image = self.def_image        
        if self.state < 2:
            if pygame.time.get_ticks() - self.time > 3000:
                self.seq[self.state] = self.pos
                self.state += 1
                self.pos = self.seq[self.state % 2]
                self.time = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.time > 12000:
            self.state = 0
            self.time = pygame.time.get_ticks()
            self.call()

    def call(self):
        self.Map.layers.append(self.layer)
        self.Map.layers[0].reset()
        for bridge in self.arena.bridges:
            bridge.update()
        a, b = self.seq
        if a == 0:
            self.pl.call(b)
        if b == 2:
            self.arena.new(a)
        else:
            rand, free = self.arena.get_random(a)
            if b == 1:
                rand.make(True, self.pl)
            elif b == 3 and free:
                self.arena.reduce(a)
                if a:
                    bridges = (self.arena.bridgesB, self.arena.bridgesA, self.arena.bridgesC)[a - 1]
                    rand.delete(self.pl, bridges, self.arena.bridges)
                else:
                    rand.delete(self.pl, self.arena.rooms)
            else:
                if a:
                    bridges = (self.arena.bridgesB, self.arena.bridgesA, self.arena.bridgesC)[a - 1]
                    rand.delete(self.pl, bridges, self.arena.bridges)
                else:
                    rand.delete(self.pl, self.arena.rooms)
                self.arena.new(a)                
        self.layer.blit()
        del self.Map.layers[-1]

    def tiles(self):
        for y in range(self.h):
            for x in range(self.w):
                yield (self.x + x, self.y + y)

    def connect(self, bridge):
        self.bridges[bridge.size].append(bridge)

    def disconnect(self, bridge):
        del self.bridges[bridge.size][self.bridges[bridge.size].index(bridge)]

    def make(self, arg, player):
        self.Map.write_on(self.tiles(), "walls", 0, None, True)
        point = (player.x // 10, player.y // 10)
        move = point in self
        self.w = random.randint(5, 10)
        self.h = random.randint(5, 10)
        self.x = random.randint(0, self.WIDTH - self.w)
        self.x = random.randint(0, self.HEIGHT - self.h)
        self.Map.write_on(self.tiles(), "walls", 1, None, True)
        for k in self.bridges:
            for bridge in self.bridges[k]:
                bridge.make(True, player)
        if move:
            px, py = random.choice(list(self.tiles))
            player.set_position(px * 10, py * 10)

    def delete(self, player, rooms):
        self.Map.write_on(self.tiles(), "walls", 0, None, True)
        point = (player.x // 10, player.y // 10)
        move = point in self
        del rooms[rooms.index(self)]
        if move:
            px, py = random.choice(list(self.tiles))
            player.set_position(*random.choice(list(random.choice(rooms).tiles())))
        for k in self.bridges:
            for bridge in self.bridges[k]:
                room = random.choice(rooms)
                while not bridge.both(self, room):
                    room = random.choice(rooms)
                bridge.set_anot(self, room)
                bridge.make(True, player)
                room.connect(bridge)

class Bridge:
    def __init__(self, room1, room2, size, Map):
        self.room1 = room1
        self.room2 = room2
        self.size = size
        self.Map = Map
        self.tiles = []
        self.make(False)

    def update(self):
        self.Map.write_on(self.tiles, "walls", 0, "wall", True)        

    def make(self, map_built, player=None):
        move = False
        if map_built:
            point = (player.x // 10, player.y // 10)
            for tile in self.tiles:
                if tile == point:
                    move = True
        room1 = self.room1
        room2 = self.room2
        size = self.size
        Map = self.Map
        self.Map.write_on(self.tiles, "walls", 0, None, True)
        right = min(room1.x + room1.w, room2.x + room2.w)
        left = max(room1.x, room2.x)
        down = min(room1.y + room1.h, room2.y + room2.h)
        up = max(room1.y, room2.y)
        if right - left - size >= 0:
            x = random.randint(left, right - size)
            y = down
            for dy in range(up - down):
                for dx in range(size):
                    self.tiles.append((x + dx, y + dy))
        elif down - up - size >= 0:
            x = right
            y = random.randint(up, down - size)
            for dy in range(size):
                for dx in range(left - right):
                    self.tiles.append((x + dx, y + dy))
        else:
            up = room1.y < room2.y
            left = room1.x < room2.x
            if left:
                x1 = room1.x + room1.w
                x2 = random.randint(room2.x, room2.x + room2.w - size)
                y1 = random.randint(room1.y, room1.y + room1.h - size)
                r1 = (x1, y1, x2 - x1, size)
                x1 = x2
            else:
                x1 = random.randint(room2.x, room2.x + room2.w - size)
                x2 = room1.x
                y1 = random.randint(room1.y, room1.y + room1.h - size)
                r1 = (x1, y1, x2 - x1, size)
            if up:
                y2 = room2.y
            else:
                y2 = y1 + size
                y1 = room2.y + room2.h
            r2 = (x1, y1, size, y2 - y1)
            for dy in range(r1[3]):
                for dx in range(r1[2]):
                    self.tiles.append((r1[0] + dx, r1[1] + dy))
            for dy in range(r2[3]):
                for dx in range(r2[2]):
                    self.tiles.append((r2[0] + dx, r2[1] + dy))
        if move:
            px, py = random.choice(self.tiles)
            player.set_position(px * 10, py * 10)
        if map_built:
            self.check()
        else:
            self.update()

    def check(self):
        tiles = self.tiles[:]
        self.tiles = []
        for tile in tiles:
            not_in_room = True
            for room in self.Map.rooms:
                if tile in room:
                    not_in_room = False
            if not_in_room:
                self.tiles.append(tile)

    def delete(self, player, bridges, all_bridges):
        del bridges[bridges.index(self)]
        del all_bridges[all_bridges.index(self)]
        self.Map.write_on(self.tiles, "walls", 0, None, True)
        move = False
        point = (player.x // 10, player.y // 10)
        for tile in self.tiles:
            if tile == point:
                move = True
        if move:
            px, py = random.choice(list(self.room1.tiles()))
            player.set_position(px * 10, py * 10)
        self.room1.disconnect(self)
        self.room2.disconnect(self)

    def set_anot(self, room1, room2):
        if room1 == self.room1:
            self.room1 = room2
        else:
            self.room2 = room2

    def both(self, room1, room2):
        return self.room1 == room1 and self.room2 == room2 or self.room2 == room1 and self.room1 == room2

    def fill(self, n):
        self.Map.write_on(self.tiles, "walls", n, None, True)

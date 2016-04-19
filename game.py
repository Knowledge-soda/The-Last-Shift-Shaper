import cProfile
import random

import pygame
from Mind import *

from doc.src import main

pygame.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

        self.PLACES = [Imagination.PLACE() for x in range(3)]
        self.last = self.PLACES[0]
        self.game = Imagination.Game(self.PLACES[0])

        self.keyboard = Imagination.Keyboard(Imagination.ARROWS +
          Imagination.HIT + [(pygame.K_ESCAPE, "menu"),
          (pygame.K_F1, "help"), (pygame.K_F2, "flip"),
          (pygame.K_LSHIFT, "shift"), (pygame.K_RSHIFT, "shift"),
          (pygame.K_LCTRL, "fire"), (pygame.K_RCTRL, "fire")])
        self.game.declare(type_=Imagination.Vertical_menu, distance=200,
          keyboard=self.keyboard)
        self.font = pygame.font.SysFont(None, 48)
        self.game.define(type_=Imagination.text_option, font=self.font,
          color=(255, 255, 0), pos_do=Imagination.ch_color((255, 0, 0)),
          anti_pos_do=Imagination.reset())

        self.Main_menu = self.game.set_from(places=self.PLACES[0])

        self.Main_menu.set_from(True, text="Start", do=self.link(self.PLACES[1]))
        self.Main_menu.set_from(text="Something")
        self.Main_menu.set_from(text="Quit", do=Imagination.Quit)

        self.Main_menu.set_options()

        self.Game_menu = self.game.set_from(places=self.PLACES[2])

        self.Game_menu.set_from(True, text="Continue", do=self.go_to_last)
        self.Game_menu.set_from(text="Main Menu", do=self.link(self.PLACES[0]))
        self.Game_menu.set_from(text="Quit", do=Imagination.Quit)

        self.Game_menu.set_options()

        self.arena = main.Arena(self)

        self.Clock = pygame.time.Clock()
        
    def main(self):
        while self.game.run():
            if self.keyboard["help"] == 1:
                cProfile.run("game.run()", "debug.txt")
            else:
                game.run()

    def run(self):
        if not self.PLACES[2]:
            if self.keyboard["menu"]:
                self.game.change(self.PLACES[2])

        self.screen.fill((0, 0, 50))

        self.game.blit()

        if self.PLACES[1]:
            self.arena.blit()

        self.Clock.tick(60)

        pygame.display.flip()

    def link(self, place):
        def f(obj, push):
            self.last = place
            self.game.change(place)
        return f

    def go_to_last(self, obj, push):
        self.game.change(self.last)

game = Game()
game.main()
pygame.quit()

from source.PenguinJump.main import *
from source.SnowRider.game import *
import json

with open('./source/guide.json') as text:
    data = json.load(text)


class Menu:
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h = self.game.WEIGHT / 2, self.game.HEIGHT / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 150, 150)
        self.offset = - 100

    def draw_cursor(self):
        self.game.draw_text('*', 15, self.cursor_rect.x + 27, self.cursor_rect.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0))
        pygame.display.update()
        self.game.reset_keys()


class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Start PenguinJump"
        self.start1x, self.start1y = self.mid_w, self.mid_h + 30
        self.start2x, self.start2y = self.mid_w, self.mid_h + 55
        self.guidex, self.guidey = self.mid_w, self.mid_h + 90
        self.cursor_rect.midtop = (self.start1x + self.offset, self.start1y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLUE)
            self.game.draw_text('Winter Games', 40, self.game.WEIGHT / 2, self.game.HEIGHT / 2 - 40)
            self.game.draw_text("< > Start PenguinJump  ", 15, self.start1x, self.start1y)
            self.game.draw_text("< > Start SnowRide  ", 15, self.start2x, self.start2y)
            self.game.draw_text("< > Guide   ", 15, self.guidex, self.guidey)
            self.game.draw_text('Use ArrowKeys to shift, Enter to select', 12,
                                self.game.WEIGHT / 2, self.game.HEIGHT - 120)
            self.game.draw_text('Press ESC - to quit the Menu', 12, self.game.WEIGHT / 2, self.game.HEIGHT - 100)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == 'Start PenguinJump':
                self.cursor_rect.midtop = (self.start2x + self.offset + 21, self.start2y)
                self.state = 'Start SnowRide'
            elif self.state == 'Start SnowRide':
                self.cursor_rect.midtop = (self.guidex + self.offset + 81, self.guidey)
                self.state = 'Guide'
            elif self.state == 'Guide':
                self.cursor_rect.midtop = (self.start1x + self.offset, self.start1y)
                self.state = 'Start PenguinJump'
        elif self.game.UP_KEY:
            if self.state == 'Start PenguinJump':
                self.cursor_rect.midtop = (self.guidex + self.offset + 81, self.guidey)
                self.state = 'Guide'
            elif self.state == 'Start SnowRide':
                self.cursor_rect.midtop = (self.start1x + self.offset, self.start1y)
                self.state = 'Start PenguinJump'
            elif self.state == 'Guide':
                self.cursor_rect.midtop = (self.start2x + self.offset + 21, self.start2y)
                self.state = 'Start SnowRide'

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == 'Start PenguinJump':
                maincast()
            elif self.state == 'Start SnowRide':
                snowrider()
            elif self.state == 'Guide':
                self.game.curr_menu = self.game.Guide
            self.run_display = False


class GuideMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.BLUE)
            self.game.draw_text('Guide', 20, self.game.WEIGHT / 2, self.game.HEIGHT / 7 - 50)
            c = 0
            for x in range(len(data)):
                self.game.draw_text(data[x], 8, self.game.WEIGHT / 2, self.game.HEIGHT / 5 + c)
                c += 15

            self.game.draw_text('Press ESC - to quit the Menu', 10, self.game.WEIGHT / 2, self.game.HEIGHT - 200)
            self.game.draw_text('Press Enter - to return', 10, self.game.WEIGHT / 2, self.game.HEIGHT - 220)
            self.game.draw_text('powered with pygame.', 13, self.game.WEIGHT / 2, self.game.HEIGHT / 2 + 300)
            self.game.draw_text('(c) 2022 Winter Games. All rights reserved.', 13, self.game.WEIGHT / 2,
                                self.game.HEIGHT / 2 + 320)
            self.blit_screen()
            

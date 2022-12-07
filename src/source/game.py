from source.menu import *


class Game:
    def __init__(self):
        pygame.display.set_caption("Winter Games")
        game_dir = os.path.dirname(__file__)
        game_dir = os.path.join(game_dir, "SnowRider")
        data_dir = os.path.join(game_dir, "data")
        img_dir = os.path.join(data_dir, "img")
        font_dir = os.path.join(data_dir, "font")
        pygame.init()
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.WEIGHT, self.HEIGHT = 600, 680
        self.display = pygame.Surface((self.WEIGHT, self.HEIGHT))
        self.window = pygame.display.set_mode((self.WEIGHT, self.HEIGHT))
        self.font_name = os.path.join(font_dir, "prstartk.ttf")
        self.BLUE, self.WHITE = (44, 0, 128), (255, 255, 255)
        self.main_menu = MainMenu(self)
        self.Guide = GuideMenu(self)
        self.curr_menu = self.main_menu

        def load_png(file, directory, scale, convert_alpha=False):
            path = os.path.join(directory, file)
            if not convert_alpha:
                img = pygame.image.load(path).convert_alpha()
            else:
                img = pygame.image.load(path).convert()
                trans_color = img.get_at((0, 0))
                img.set_colorkey(trans_color)
            img_w = img.get_width()
            img_h = img.get_height()
            img = pygame.transform.scale(img, (img_w * scale, img_h * scale))
            return img

        window_icon = load_png("icon.png", img_dir, 5)
        pygame.display.set_icon(window_icon)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running, self.playing = False, False
                    self.curr_menu.run_display = False
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def draw_text(self, text, size, x, y):
        pygame.font.init()
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)
        
    def run(self):
        while self.running:
            self.curr_menu.display_menu()
            

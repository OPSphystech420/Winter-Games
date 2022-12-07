import os
from os import path, environ
from source.PenguinJump.Sprites import *
from source.PenguinJump.JsonInit import *


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


class Game1:

    def __init__(self):
        data = Config.load_json('./source/PenguinJump/settings.json')
         # Initialize game window
        self.all_Sprites = None
        self.dir = None
        self.highscore = None
        self.spritesheet = None
        self.LEFT_KEY = None
        self.RIGHT_KEY = None
        self.UP_KEY = None
        self.DOWN_KEY = None
        self.sound_dir = None
        self.jump_sound = None
        self.bounce_sound = None
        self.hurt_sound = None
        self.select_sound = None
        self.press_sound = None
        self.flap_sound = None
        self.falling_sound = None
        self.lose_sound = None
        self.up_sound = None
        self.snowflakes = None
        self.stars = None
        self.option_cursor = None
        self.select_cursor = None
        self.gameOver_cursors = None
        self.shootingStar = None
        self.shootingStar2 = None
        self.last_update = None
        self.objects = None
        self.last_spawn = None
        self.playing = None
        self.player = None
        self.seagulls = None
        self.platforms = None
        self.balloons = None
        self.enemies = None
        self.score = None
        pygame.mixer.pre_init(44100, -16, 2, 2048)  # Prevents delay in jumping sound
        pygame.init()
        pygame.mixer.init(frequency=44100)
        self.monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
        environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (
            self.monitor_size[0] / 2 - data.SCREEN_WIDTH / 2, self.monitor_size[1] / 2 - data.SCREEN_HEIGHT / 2)
        self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT))
        self.full_screen = False
        pygame.display.set_caption(data.TITLE)
        self.VOLUME_SETTING = 100
        self.volume_mult = 1
        self.clock = pygame.time.Clock()
        self.running = True
        self.FONT_NAME = data.FONT

        # Load saved data
        self.load_data()
        self.start_image = pygame.image.load("source/PenguinJump/Sprites/start_screen.png")
        pygame.mixer.music.load(path.join(self.sound_dir, "little march.ogg"))
        self.water = pygame.image.load("source/PenguinJump/Sprites/water2.png")
        self.mountains = pygame.image.load("source/PenguinJump/Sprites/mountains.png")
        self.moon = pygame.transform.scale(pygame.image.load("source/PenguinJump/Sprites/moon.png"), (45, 45))
        self.play_again = True
        self.jump_range = 50
        self.spawn_y = 0
        self.plat_chance = 10
        self.balloon_chance = 1000
        self.last_score = 0

    def reset(self):
        self.press_sound.play()
        # Display The Ready Screen
        self.ready_screen()
        if not self.running:
            return
        self.score = 0
        # Initialize non-player sprites
        self.all_Sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.balloons = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.seagulls = pygame.sprite.Group()
        self.objects = pygame.sprite.Group()

        # Spawn the player
        self.player = Player(self)  # Reference all the games variables to the player as well
        self.all_Sprites.add(self.player)

        for plat in data.platform_list:
            p = Platform(self, plat[0], plat[0], self.platforms, self.all_Sprites)  # * explodes the list
            self.last_spawn = p

        pygame.mixer.music.load(path.join(self.sound_dir, "theme.ogg"))
        # self.orca = orca(self)
        self.game()

    def game(self):
        # main game loop
        pygame.mixer.music.play(loops=-1)  # Start the music loop
        self.playing = True
        while self.playing:
            self.clock.tick(data.FPS)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(50)  # Fade out over half a second

    def update(self):
        # Game loop update
        self.all_Sprites.update()
        self.collision_check()
        self.platform_spawn()
        self.scroll_up()
        self.scroll_down()
        self.seagull_spawn()
        self.increase_difficulty()
        # Check for game over
        self.check_death()
        # Check if player reaches the top of the screen

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.VIDEORESIZE:
                if not self.full_screen:
                    self.screen = pygame.display.set_mode((event.w, event.h))
            if event.type == pygame.KEYDOWN:  # better method for keeping track of how many times space is pressed
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.pause()
                if event.key == pygame.K_F5:
                    self.full_screen = not self.full_screen
                    if self.full_screen:
                        self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT))
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and not self.player.bouncing and not self.player.plummeting \
                        and not self.player.stun and not self.player.got_balloon:
                    self.player.velocity.y = 0  # also gives the flap effect
                    self.player.space_pressed += 1
                    if self.player.space_pressed > 1:
                        self.flap_sound.play()

    def pause(self):
        paused = True
        pygame.mixer.pause()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False
                    self.running = False
                    paused = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.playing = False
                        self.running = False
                        return
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        pygame.mixer.unpause()
                        paused = False
                    if event.key == pygame.K_F5:
                        self.full_screen = not self.full_screen
                        if self.full_screen:
                            self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT))
            self.draw_text("PAUSED", 24, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2)
            pygame.display.flip()

    def draw(self):
        self.screen.fill((47, 55, 150))
        self.screen.blit(self.water, (0, 400))
        self.screen.blit(self.moon, (530, 50))
        self.screen.blit(self.mountains, (0, 300))
        self.snoweffect()
        self.all_Sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)  # always draw the player last so they aren't overshadowed
        self.draw_text(str(self.score), 22, data.white, data.SCREEN_WIDTH / 2, 15)
        pygame.display.flip()

    def increase_difficulty(self):
        if self.score - self.last_score > 100:
            self.last_score = self.score
            self.plat_chance += 5
            self.balloon_chance += 10

    def check_death(self):
        if len(self.platforms) == 0 and not self.player.plummeting:
            self.player.plummeting = True
            self.falling_sound.play()

        if self.player.rect.top > data.SCREEN_HEIGHT:  # If the top of the player hits the bottom screen, its game over
            self.falling_sound.stop()
            self.player.kill()
            for sprite in self.all_Sprites:
                # sprite.rect.y -= max(self.player.velocity.y,10) # Make platforms
                if sprite.rect.bottom < 0:  # Kill any sprites that are no longer on screen
                    sprite.kill()
        if len(self.all_Sprites) == 0:  # When all sprites are killed, reset the game
            self.lose_sound.play()
            self.playing = False

    def collision_check(self):
        # Check if the player hits a platform, but only when falling
        global hit
        if self.player.velocity.y > 0 and not self.player.got_balloon:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False, )
            if hits:
                self.player.stun = False
                # Snap to the lowest platform that the player has collided with
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.y < lowest.rect.bottom:  # Only snap to the platform if the player is above it
                    self.player.pos.y = lowest.rect.top
                    self.player.velocity.y = 0
                    self.player.rect.midbottom = self.player.pos  # Keeps the player from jiggling by updating the
                    # player rect before drawing
                    self.player.jumping = False
                    self.player.space_pressed = 0
                    hit.touched = True
        enems = pygame.sprite.spritecollide(self.player, self.enemies, False, )
        if enems and not self.player.stun and not self.player.got_balloon:
            if self.player.pos.y < enems[0].rect.bottom and self.player.velocity.y > 0:
                if type(enems[0]).__name__ == "seagull":
                    self.bounce_seagull(enems[0])
                else:
                    self.bounce()
            else:
                self.knockback(self.player)
        power_up = pygame.sprite.spritecollide(self.player, self.balloons, False, )
        if power_up and not self.player.stun:
            power_up[0].used = True
            self.player.got_balloon = True

    def knockback(self, player):
        if not self.player.bouncing:
            self.hurt_sound.play()
            player.stun = True
            player.velocity.y -= 12
            if player.velocity.x >= 0:
                player.velocity.x = -25
            else:
                player.velocity.x = 25

    def bounce(self):
        self.bounce_sound.play()
        self.player.bouncing = True
        self.player.velocity.y = -30

    def bounce_seagull(self, seagull):
        seagull.hit = True
        self.bounce_sound.play()
        self.player.bouncing = True
        self.player.velocity.y = -15

    # Checks if the camera needs to scroll up
    def scroll_up(self):
        if self.player.rect.top <= data.SCREEN_HEIGHT * .35:
            self.player.pos.y += max(abs(self.player.velocity.y), 5)  # Move the player's position
            self.spawn_y += max(abs(self.player.velocity.y), 5)
            self.add_score()
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.velocity.y),
                                   5)  # Platforms should move at the same speed as the player
                if plat.rect.top >= data.SCREEN_HEIGHT:  # If the platform goes offscreen, delete it
                    if plat.hasSeal:
                        plat.seal.kill()
                    if plat.hasWalrus:
                        plat.walrus.kill()
                    if plat.hasSnowman:
                        plat.snowman.kill()
                    plat.kill()

            for enemy in self.enemies:
                enemy.rect.y += max(abs(self.player.velocity.y),
                                    5)  # Platforms should move at the same speed as the player
                if enemy.rect.top >= data.SCREEN_HEIGHT:  # and not type(enemy).__name__ =='orca':  # If the platform goes
                    # offscreen, delete it
                    enemy.kill()
                    # self.score += 10
            for object in self.objects:
                object.rect.y += max(abs(self.player.velocity.y),
                                     5)  # Platforms should move at the same speed as the player
                if object.rect.top >= data.SCREEN_HEIGHT:  # If the platform goes offscreen, delete it
                    object.kill()

    # Checks if the camera needs to scroll down
    def scroll_down(self):
        if self.player.rect.bottom >= data.SCREEN_HEIGHT * 3 / 4:
            self.player.pos.y -= abs(self.player.velocity.y)
            for plat in self.platforms:
                plat.rect.y -= abs(self.player.velocity.y)
                if plat.rect.y < -data.SCREEN_HEIGHT / 2:
                    plat.kill()
            for enemy in self.enemies:
                enemy.rect.y -= abs(self.player.velocity.y)
            for object in self.objects:
                object.rect.y -= abs(self.player.velocity.y)

    def add_score(self):
        if self.player.velocity.y < 0:
            self.score += abs(self.player.velocity.y / 12)
            self.score = truncate(self.score, 3)
            if int(self.score) % 210 < 10:
                self.plat_chance += 1

    def platform_spawn(self):
        width = random.randrange(100, 150)  # get random with of the platform from the screen
        if self.last_spawn.rect.y > 0:
            if self.spawn_y > self.jump_range:
                self.spawn_y = 0
                self.last_spawn = Platform(self, random.randrange(0, data.SCREEN_WIDTH - width),
                                           random.randrange(-130, -100), self.platforms,
                                           self.all_Sprites)  # Spawn above the window
            elif self.spawn_y > 20:
                if random.randint(1, self.plat_chance) == 1:
                    self.spawn_y = 0
                    Platform(self, random.randrange(0, data.SCREEN_WIDTH - width),
                             random.randrange(-130, -100), self.platforms, self.all_Sprites)  # Spawn above the window

    def seagull_spawn(self):
        if len(self.seagulls) < 1:
            if int(self.score) % 210 < 10:
                Seagull(self)
        if len(self.balloons) < 1:
            if random.randint(1, self.balloon_chance) == 1:
                Balloon(self)

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.FONT_NAME, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def start_screen(self):
        waiting = True
        self.select_cursor = Cursor(self)
        self.start_menu_stars()
        while waiting:
            self.screen.blit(self.start_image, (0, 0))
            for star in self.stars:
                star.draw_star()
            self.select_cursor.draw_cursor()
            self.draw_text(data.TITLE, 48, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 4 + 20)
            # self.draw_text("A and D to move, Space to Jump", 18, data.white, data.SCREEN_WIDTH/2, data.SCREEN_HEIGHT/2 )
            self.draw_text("START", 15, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT * 3 / 4)
            self.draw_text("OPTIONS", 15, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT * 3 / 4 + 30)
            self.draw_text("powered by pygame.", 8, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT * 3 / 4 + 120)
            self.draw_text("Music Created with BeepBox. Sound Effects Created with Bfxr. Art Created with "
                           "Texturepacker.", 6, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT * 3 / 4 + 140)
            self.draw_text("(c) 2022 PenguinJump. All rights reserved.",
                           8, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT * 3 / 4 + 130)
            self.draw_text("High Score: " + str(self.highscore), 15, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 4 + 105)

            pygame.display.flip()  # Print the contents to the screen
            waiting = self.wait_for_key("start")

    def wait_for_key(self, mode):
        waiting = True
        for event in pygame.event.get():
            if mode == "start":
                self.select_cursor.move_cursor(event)
            else:
                pass
            if event.type == pygame.QUIT:
                waiting = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                if event.key == pygame.K_F5:
                    self.full_screen = not self.full_screen
                    if self.full_screen:
                        self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT))
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if mode == "options":
                        self.options_select()
                    else:
                        waiting = False
                elif (event.key == self.UP_KEY or event.key == self.DOWN_KEY) and mode == "options":
                    self.select_cursor.move_cursor_options(event)
                elif event.key == pygame.K_BACKSPACE and mode == "options":
                    waiting = False
        return waiting

    def update_high_score(self):
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("New High Score!", 15, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2 + 40)
            with open(path.join(self.dir, data.HS_FILE), 'w') as file:
                file.write(str(self.highscore))
        else:
            self.draw_text("High Score: " + str(self.highscore), 15, data.white, data.SCREEN_WIDTH / 2, 15)

    def load_data(self):
        self.dir = path.dirname(path.abspath("game.py"))  # Gets the directory name of the game.py file
        img_dir = path.join(self.dir, "source/PenguinJump/Sprites")
        if os.path.exists(path.join(self.dir, data.HS_FILE)):
            mode = 'r+'
        else:
            mode = 'a+'
        try:
            with open(path.join(self.dir, data.HS_FILE),
                      mode) as file:  # open highscore file, w allows us to write the file and creates it if doesnt
                # exist
                # Read the highscore only if it exists
                self.highscore = float(file.read())
        except (OSError, ValueError):
            self.highscore = 0  # If file isnt read, use 0

        # Load the spritesheet
        self.spritesheet = Spritesheet(path.join(img_dir, data.SPRITESHEET))

        # Load the snow
        self.initialize_snow()

        # Load controls
        self.LEFT_KEY = pygame.K_a
        self.RIGHT_KEY = pygame.K_d
        self.UP_KEY = pygame.K_w
        self.DOWN_KEY = pygame.K_s

        # load sounds
        self.sound_dir = path.join(self.dir, "source/PenguinJump/sound")
        self.jump_sound = pygame.mixer.Sound(path.join(self.sound_dir, "Jump8.wav"))
        self.jump_sound.set_volume(.1)
        self.bounce_sound = pygame.mixer.Sound(path.join(self.sound_dir, "Bounce.wav"))
        self.bounce_sound.set_volume(.1)
        self.hurt_sound = pygame.mixer.Sound(path.join(self.sound_dir, "Hurt.wav"))
        self.hurt_sound.set_volume(.1)
        self.select_sound = pygame.mixer.Sound(path.join(self.sound_dir, "Cursor_Select.wav"))
        self.select_sound.set_volume(.1)
        self.press_sound = pygame.mixer.Sound(path.join(self.sound_dir, "Press_Sound.wav"))
        self.press_sound.set_volume(.1)
        self.flap_sound = pygame.mixer.Sound(path.join(self.sound_dir, "flap.wav"))
        self.flap_sound.set_volume(.1)
        self.falling_sound = pygame.mixer.Sound(path.join(self.sound_dir, "falling.wav"))
        self.falling_sound.set_volume(.5)
        self.lose_sound = pygame.mixer.Sound(path.join(self.sound_dir, "lose.wav"))
        self.lose_sound.set_volume(.5)
        self.up_sound = pygame.mixer.Sound(path.join(self.sound_dir, "fly_away.wav"))
        self.up_sound.set_volume(.5)

    def initialize_snow(self):
        # Initialize snow array
        self.snowflakes = []
        for i in range(200):
            self.snowflakes.append(Snow(self))

    def snoweffect(self):
        for s in self.snowflakes:
            s.y += 1.5
            if s.y > data.SCREEN_HEIGHT:
                s.x = random.randrange(0, data.SCREEN_WIDTH)
                s.y = random.randrange(-50, -10)
            s.draw_snow()

    def start_menu_stars(self):
        self.stars = []
        for i in range(100):
            self.stars.append(Star(self, random.randrange(0, data.SCREEN_WIDTH), random.randrange(100, 390)))
        for i in range(30):
            self.stars.append(Star(self, random.randrange(200, 400), random.randrange(10, 150)))

    def options_menu(self):
        waiting = True
        self.option_cursor = Cursor(self)
        self.press_sound.play()
        self.select_cursor = Cursor(self)
        self.select_cursor.selected = "VOLUME"
        self.select_cursor.offset = -125
        self.select_cursor.x = data.SCREEN_WIDTH / 2 + self.select_cursor.offset
        self.select_cursor.y = data.SCREEN_HEIGHT / 2
        while waiting:
            if not self.running:
                return

            self.screen.fill(data.black)
            self.snoweffect()
            self.select_cursor.draw_cursor()
            self.draw_text("OPTIONS", 48, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 4)
            self.draw_text("VOLUME", 18, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2)
            self.draw_text("CONTROLS", 18, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2 + 30)
            self.draw_text("Press Backspace to return", 12, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT - 80)
            self.draw_text("Press F5 to enter full_screen Mode", 12, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT - 100)
            pygame.display.flip()  # Print the contents to the screen
            waiting = self.wait_for_key("options")

    def options_select(self):
        option = self.select_cursor.selected
        if option == "VOLUME":
            self.press_sound.play()
            self.volume_control()
        elif option == "CONTROLS":
            self.press_sound.play()
            self.change_controls()

    def volume_control(self):
        selected = False
        self.option_cursor.selected = "LOWER"
        self.option_cursor.x = data.SCREEN_WIDTH / 4 + self.option_cursor.offset
        self.option_cursor.y = data.SCREEN_HEIGHT / 2 + 80
        while not selected:
            self.screen.fill(data.black)
            self.snoweffect()
            self.draw_text("OPTIONS", 48, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 4)
            self.draw_text("VOLUME", 18, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2)
            self.draw_text("-", 18, data.white, data.SCREEN_WIDTH / 4, data.SCREEN_HEIGHT / 2 + 80)
            self.draw_text("+", 18, data.white, data.SCREEN_WIDTH * 3 / 4, data.SCREEN_HEIGHT / 2 + 80)
            self.draw_text(str(self.VOLUME_SETTING) + '%', 18, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2 + 80)
            self.option_cursor.draw_cursor()
            selected = self.option_cursor.control_option_sound()
            self.adjust_sounds()

            pygame.display.flip()  # Print the contents to the screen

    def adjust_sounds(self):
        pygame.mixer.music.set_volume(self.volume_mult)
        self.jump_sound.set_volume(.1 * self.volume_mult)
        self.bounce_sound.set_volume(.1 * self.volume_mult)
        self.hurt_sound.set_volume(.1 * self.volume_mult)
        self.select_sound.set_volume(.1 * self.volume_mult)
        self.press_sound.set_volume(.1 * self.volume_mult)
        self.falling_sound.set_volume(.5 * self.volume_mult)
        self.flap_sound.set_volume(.1 * self.volume_mult)
        self.lose_sound.set_volume(.5 * self.volume_mult)
        self.up_sound.set_volume(.5 * self.volume_mult)

    def change_controls(self):
        selected = False
        self.option_cursor.selected = "ASDW"
        self.option_cursor.x = data.SCREEN_WIDTH / 4 + self.option_cursor.offset
        self.option_cursor.y = data.SCREEN_HEIGHT / 2 + 80
        while not selected:
            self.screen.fill(data.black)
            self.snoweffect()
            self.draw_text("OPTIONS", 48, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 4)
            self.draw_text("CONTROLS", 18, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2 + 30)
            self.draw_text("ASDW", 18, data.white, data.SCREEN_WIDTH / 4, data.SCREEN_HEIGHT / 2 + 80)
            self.draw_text("Arrow Keys", 18, data.white, data.SCREEN_WIDTH * 3 / 4, data.SCREEN_HEIGHT / 2 + 80)
            self.option_cursor.draw_cursor()
            selected = self.option_cursor.control_option_cursor()
            pygame.display.flip()  # Print the contents to the screen

    def gameover(self):
        # Prevent the Game over screen when the user exits out

        pygame.mixer.music.load(path.join(self.sound_dir, "tired march.ogg"))
        pygame.mixer.music.set_volume(.7 * self.volume_mult)
        pygame.mixer.music.play(-1)
        self.gameOver_cursors = Cursor(self)
        selected = False
        self.gameOver_cursors.offset = -175
        self.gameOver_cursors.x = data.SCREEN_WIDTH / 2 + self.gameOver_cursors.offset
        self.gameOver_cursors.y = data.SCREEN_HEIGHT / 2

        while not selected:

            if not self.running:
                return
            self.screen.fill(data.black)
            self.snoweffect()
            self.draw_text("GAME OVER", 48, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 4)
            self.draw_text("Score:" + str(self.score), 22, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT * 3 / 4)
            self.draw_text("PLAY AGAIN", 18, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2)
            self.draw_text("RETURN TO MENU", 18, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2 + 30)
            self.gameOver_cursors.draw_cursor()
            pygame.display.flip()
            selected = self.gameOver_cursors.gameover_cursor()
            self.update_high_score()

        if self.gameOver_cursors.selectedGO == "PLAY_AGAIN":
            self.play_again = True
        else:
            self.play_again = False

    def logo_screen(self):
        now = pygame.time.get_ticks()
        colors = 0
        self.shootingStar = ShootingStar(self, data.SCREEN_WIDTH, -60)
        self.shootingStar2 = ShootingStar(self, data.SCREEN_WIDTH + 50, -60)
        while now < 6750:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.playing = False
                        self.running = False
                        return
                    if event.key == pygame.K_F5:
                        self.full_screen = not self.full_screen
                        if self.full_screen:
                            self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT))

            self.screen.fill(data.black)
            if now > 1000:
                self.shootingStar.move()
                self.shootingStar.draw()
            if now > 1500:
                self.shootingStar2.move()
                self.shootingStar2.draw()
            self.draw_text("PenguinJump", 18, (colors, colors, colors), data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2)
            self.draw_text("(c) 2022 All Rights Reserved", 10, (colors, colors, colors), data.SCREEN_WIDTH / 2,
                           data.SCREEN_HEIGHT / 2 + 30)
            if (colors <= 255) and now < 4000:
                colors += .2
            elif now > 3000:
                if colors >= 0:
                    colors -= .22
                else:
                    colors = 0

            pygame.display.flip()
            now = pygame.time.get_ticks()

    def ready_screen(self):
        pygame.mixer.music.set_volume(self.volume_mult)
        pygame.mixer.music.load(path.join(self.sound_dir, "march_sound.ogg"))
        pygame.mixer.music.play(1)
        now = pygame.time.get_ticks()
        self.last_update = pygame.time.get_ticks()
        while now - self.last_update < 2700:
            self.clock.tick(data.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            now = pygame.time.get_ticks()
            self.screen.fill(data.black)
            self.snoweffect()
            self.draw_text("How High Can You Fly?", 24, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2 - 50)
            self.draw_text("High Score: " + str(self.highscore), 15, data.white, data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2 + 30)
            pygame.display.flip()
            

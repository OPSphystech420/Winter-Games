# Sprite classes
import random
import pygame

from source.PenguinJump.JsonInit import *

vec = pygame.math.Vector2
data = Config.load_json('./source/PenguinJump/settings.json')

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        self.seconds = None
        self.leftFrames = None
        self.rightFrames = None
        self.stun_frames = None
        self.game = game  # player now has reference to everything in the game
        pygame.sprite.Sprite.__init__(self)
        self.image = game.spritesheet.get_image(372, 23, 30, 40)
        self.rect = self.image.get_rect()
        self.rect.center = (data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2)
        # Instead of x and y coordinates, we will have a position, velocity, and acceleration vector of (x,y)
        self.pos = vec(data.SCREEN_WIDTH / 2, data.SCREEN_HEIGHT / 2)
        self.velocity = vec(0, 0)
        self.acc = vec(0, 0)
        self.walking = False
        self.current_frame = 0
        self.last_update = 0
        self.last_pos = 0
        self.jumping = False
        self.bouncing = False
        self.stun = False
        self.load_images()
        self.plummeting = False
        self.got_balloon = False
        self.space_pressed = 0
        self.start_time = True

    def jump(self):
        # Jump only if standing on a platform
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits and not self.jumping and not self.got_balloon:
            self.game.jump_sound.play()
            self.velocity.y = data.player_jump
            self.jumping = True

    def ride_balloon(self):

        if self.start_time:
            self.seconds = pygame.time.get_ticks()
            self.start_time = False
            self.velocity.y = 2
        now = pygame.time.get_ticks()
        if now - self.seconds < 5000:
            self.acc = vec(0, -.08)
        else:
            self.got_balloon = False
            self.start_time = True

    def update(self):
        self.animate()
        self.last_pos = self.pos.y
        # Get keys pressed from the user
        self.acc = vec(0, data.gravity)  # Positive y acceleration for data.gravity
        if self.got_balloon:
            self.ride_balloon()
        keys = pygame.key.get_pressed()
        if keys[self.game.LEFT_KEY]:
            self.acc.x = -data.player_acc
        if keys[self.game.RIGHT_KEY]:
            self.acc.x = data.player_acc

        # apply friction
        self.acc.x += self.velocity.x * data.friction  # Multiply velocity times friction to adjust acceleration ( faster
        # speed, dre friction) Only in x direction
        # Newton equations of motion
        self.velocity += self.acc
        self.pos += self.velocity + (self.acc * .5)

        if self.bouncing and self.velocity.y > 0:
            self.bouncing = False

        # Wrap around the screen
        if self.pos.x > data.SCREEN_WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = data.SCREEN_WIDTH

        # update the player sprite
        self.rect.midbottom = self.pos

    def load_images(self):
        self.leftFrames = [
            self.game.spritesheet.get_image(340, 23, 30, 40),  # Left stand
            self.game.spritesheet.get_image(33, 65, 30, 40),  # Left walk
        ]  # Right walk
        self.rightFrames = [self.game.spritesheet.get_image(372, 23, 30, 40),  # Right Stand
                            self.game.spritesheet.get_image(65, 65, 30, 40)]  # Right walk
        self.stun_frames = [self.game.spritesheet.get_image(1, 65, 30, 40),
                            pygame.transform.flip(self.game.spritesheet.get_image(1, 65, 30, 40), True, False)
                            ]

    def animate(self):
        now = pygame.time.get_ticks()  # Gives us current time

        if self.got_balloon:
            if self.velocity.x > 0:
                self.image = self.game.spritesheet.get_image(339, 65, 44, 57)
            else:
                self.image = pygame.transform.flip(self.game.spritesheet.get_image(339, 65, 44, 57), True, False)
            return

        if self.stun:
            if self.velocity.x > 0:
                self.image = self.stun_frames[1]
            else:
                self.image = self.stun_frames[0]
            return

        if (self.jumping is True or self.velocity.y > 0) and now - self.last_update > 50:
            if self.velocity.x > 0:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.rightFrames)
                self.image = self.rightFrames[self.current_frame]
            else:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.leftFrames)
                self.image = self.leftFrames[self.current_frame]

        if now - self.last_update > 200:
            if self.velocity.x > 0:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.rightFrames)
                self.image = self.rightFrames[self.current_frame]
            else:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.leftFrames)
                self.image = self.leftFrames[self.current_frame]


class Platform(pygame.sprite.Sprite):
    def __init__(self, game, x, y, platformgroup, allsprites):
        self.game = game
        pygame.sprite.Sprite.__init__(self)
        imagedict = {"small": self.game.spritesheet.get_image(239, 1, 100, 20),
                     "large": self.game.spritesheet.get_image(37, 1, 200, 20)}
        images = ["small", "large"]
        self.type = random.choice(images)
        self.image = imagedict[self.type]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hasSeal = False
        self.hasWalrus = False
        self.hasSnowman = False
        platformgroup.add(self)
        allsprites.add(self)
        if self.type == "large" and random.random() <= .5 and game.score > 50:
            self.hasSeal = True
            self.seal = Seal(self.game, self)
        elif self.type == "large" and random.random() > .5 and game.score > 50:
            self.hasWalrus = True
            self.walrus = Walrus(self.game, self)
        elif self.type == "small" and random.random() <= .05:
            self.hasSnowman = True
            self.snowman = Snowman(self.game, self)


class Seagull(pygame.sprite.Sprite):
    def __init__(self, game):
        self.seagullFrameRight = None
        self.seagullFrameLeft = None
        self.groups = game.all_Sprites, game.seagulls, game.enemies  # , game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)  # Add the seagull sprite to the sprite groups
        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = game.spritesheet.get_image(65, 23, 30, 20)
        self.rect = self.image.get_rect()
        self.rect.centerx = data.SCREEN_WIDTH / 2
        self.vx = 3  # random.randrange(3,7)
        self.rect.y = random.randrange(-100, -50)
        self.hit = False
        self.falling = False

    def update(self):
        self.animate()
        self.rect.x += self.vx
        if self.falling:
            self.rect.y += 4
            return
        if self.rect.x > data.SCREEN_WIDTH:
            self.vx *= -1
        elif self.rect.x < -20:
            self.vx *= -1

    def animate(self):
        if self.hit:
            self.falling = True
            self.hit = False
            self.image = pygame.transform.flip(self.image, False, True)
        if self.falling:
            return

        now = pygame.time.get_ticks()
        if now - self.last_update > 150 and self.vx > 0:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.seagullFrameRight)
            self.image = self.seagullFrameRight[self.current_frame]
        elif now - self.last_update > 150 and self.vx < 0:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.seagullFrameLeft)
            self.image = self.seagullFrameLeft[self.current_frame]

    def load_images(self):
        self.seagullFrameRight = [self.game.spritesheet.get_image(65, 23, 30, 20),  # Seagull mid
                                  self.game.spritesheet.get_image(1, 23, 30, 20),  # Seagull Half Up
                                  self.game.spritesheet.get_image(33, 23, 30, 20),  # Seagull Up
                                  self.game.spritesheet.get_image(1, 23, 30, 20),  # Seagull half up
                                  self.game.spritesheet.get_image(65, 23, 30, 20),  # Seagull  mid
                                  self.game.spritesheet.get_image(373, 1, 30, 20),  # Seagull Wings half down
                                  self.game.spritesheet.get_image(341, 1, 30, 20),  # Seagull Wings Down
                                  self.game.spritesheet.get_image(373, 1, 30, 20)  # Seagull Wings half down
                                  ]
        # Flip the frames
        self.seagullFrameLeft = []
        for frame in self.seagullFrameRight:
            self.seagullFrameLeft.append(pygame.transform.flip(frame, True, False))


class Seal(pygame.sprite.Sprite):
    def __init__(self, game, platform):
        self.sealFrameRight = None
        self.sealFrameLeft = None
        self.groups = game.all_Sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)  # Add the seagull sprite to the sprite groups
        self.game = game
        self.plat = platform
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = game.spritesheet.get_image(97, 65, 40, 40)
        self.image.set_colorkey(data.black)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.y = self.plat.rect.top - self.rect.height
        self.vx = random.randrange(2, 5) * .5

    def load_images(self):
        self.sealFrameRight = [self.game.spritesheet.get_image(97, 65, 40, 40),  # Seal down
                               self.game.spritesheet.get_image(139, 65, 40, 40),  # Seal seal mid
                               self.game.spritesheet.get_image(181, 65, 40, 40),  # Seal up
                               self.game.spritesheet.get_image(139, 65, 40, 40),  # Seal mid
                               ]
        # Flip the frames
        self.sealFrameLeft = []
        for frame in self.sealFrameRight:
            self.sealFrameLeft.append(pygame.transform.flip(frame, True, False))

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 230 and self.vx > 0:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.sealFrameRight)
            self.image = self.sealFrameRight[self.current_frame]
        elif now - self.last_update > 230 and self.vx < 0:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.sealFrameLeft)
            self.image = self.sealFrameLeft[self.current_frame]

    def update(self):
        self.animate()
        self.rect.x += self.vx
        if self.rect.x > self.plat.rect.x + self.plat.rect.width - (self.rect.width / 2):
            self.vx *= -1
        elif self.rect.x < self.plat.rect.x - (self.rect.width / 2):
            self.vx *= -1


class Walrus(pygame.sprite.Sprite):
    def __init__(self, game, platform):
        self.WalrusFramesRight = None
        self.walrusFramesLeft = None
        self.groups = game.all_Sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)  # Add the walrus sprite to the sprite groups
        self.game = game
        self.plat = platform
        self.current_frame = 0
        self.last_update = 0
        self.image = game.spritesheet.get_image(97, 23, 79, 35)
        self.load_images()
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.y = self.plat.rect.top - self.rect.height

    def load_images(self):
        self.walrusFramesLeft = [self.game.spritesheet.get_image(97, 23, 79, 35),  # Walrus1
                                 self.game.spritesheet.get_image(178, 23, 79, 35),  # Walrus2
                                 self.game.spritesheet.get_image(259, 23, 79, 35),  # Walrus3
                                 self.game.spritesheet.get_image(178, 23, 79, 35),  # Walrus2
                                 ]
        # Flip the frames
        self.WalrusFramesRight = []
        for frame in self.WalrusFramesRight:
            self.WalrusFramesRight.append(pygame.transform.flip(frame, True, False))

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 290:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.walrusFramesLeft)
            self.image = self.walrusFramesLeft[self.current_frame]

    def update(self):
        self.animate()
        self.game.draw_text("z", 30, data.white, self.rect.x, self.rect.y)


class Orca(pygame.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_Sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_orca = pygame.transform.rotate(game.spritesheet.get_image(1, 124, 395, 200), 90)
        self.image_fin = [game.spritesheet.get_image(255, 65, 46, 48),
                          pygame.transform.flip(game.spritesheet.get_image(255, 65, 46, 48), True, False)]
        self.image = self.image_fin[0]
        self.timer = 0
        self.rect = self.image_orca.get_rect()
        self.range = random.randint(0, 205)
        self.rect.x = data.SCREEN_WIDTH / 2
        self.xvelocity = 2
        self.rect.y = 600
        self.ready = False
        self.jumping = False

        self.last_update = 0

    def update(self):

        if self.ready and not self.jumping:
            self.animatex()
        self.animatey()

    def animatex(self):
        if self.rect.x > 350:
            self.xvelocity *= -1
            self.image = self.image_fin[1]
        elif self.rect.x < 250:
            self.xvelocity *= -1
            self.image = self.image_fin[0]

        self.rect.x += self.xvelocity

    def animatey(self):
        now = pygame.time.get_ticks()
        print(self.last_update)
        if self.rect.y > data.SCREEN_HEIGHT and self.ready is False:
            print("Updating")
            self.last_update = now

        if now - self.last_update > 5000 and self.ready is False:
            if self.rect.y > 552:
                self.rect.y -= 2
            else:
                self.rect.y = 552
                self.ready = True
            return
        if 9500 < now - self.last_update < 10000 and self.ready is True:
            self.rect.y += 2
            if self.rect.y > data.SCREEN_HEIGHT:
                self.image = self.image_orca
            return
        elif now - self.last_update > 10000 and self.ready is True:
            self.jumping = True
            self.rect.y -= 5


class Snow:
    def __init__(self, game):
        self.game = game
        self.x = random.randrange(0, data.SCREEN_WIDTH)
        self.y = random.randrange(0, data.SCREEN_WIDTH)

    def draw_snow(self):
        pygame.draw.rect(self.game.screen, (255, 255, 255), (self.x, self.y, 1, 1))


class Star:
    def __init__(self, game, x, y):
        self.starimages = None
        self.game = game
        self.x = x
        self.y = y
        self.loadimages()
        self.image = game.spritesheet.get_image(1, 1, 7, 7)
        self.current_frame = random.randrange(0, len(self.starimages))
        self.last_update = 0
        self.animation_rate = random.randrange(150, 400)

    def loadimages(self):
        self.starimages = [self.game.spritesheet.get_image(1, 1, 7, 7),  # No shine
                           self.game.spritesheet.get_image(10, 1, 7, 7),  # Shine 1
                           self.game.spritesheet.get_image(19, 1, 7, 7),  # Shine 2
                           self.game.spritesheet.get_image(28, 1, 7, 7),  # Shine 3
                           self.game.spritesheet.get_image(19, 1, 7, 7),  # Shine 2
                           self.game.spritesheet.get_image(10, 1, 7, 7),  # Shine 1
                           ]

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.starimages)
            self.image = self.starimages[self.current_frame]

    def draw_star(self):
        self.animate()
        self.game.screen.blit(self.image, (self.x, self.y))


class ShootingStar:
    def __init__(self, game, x, y):
        self.game = game
        self.image = pygame.image.load("source/PenguinJump/Sprites/shootingStar.png")
        self.x = x
        self.y = y
        self.one_pass = False

    def move(self):
        self.x -= 2
        self.y += 2

    def draw(self):
        self.game.screen.blit(self.image, (self.x, self.y))


class Snowman(pygame.sprite.Sprite):
    def __init__(self, game, platform):
        self.groups = game.all_Sprites, game.objects
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = platform
        self.image = game.spritesheet.get_image(303, 65, 34, 56)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.y = self.plat.rect.top - self.rect.height


class Balloon(pygame.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_Sprites, game.objects, game.balloons
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.imageLst = [game.spritesheet.get_image(223, 65, 30, 48),
                         pygame.transform.flip(game.spritesheet.get_image(223, 65, 30, 48), True, False)]
        self.last_update = 0
        self.vy = 1
        if random.random() <= .5:
            self.vx = 1
        else:
            self.vx = -1

        if self.vx > 0:
            self.image = self.imageLst[0]
        else:
            self.image = self.imageLst[1]
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(50, data.SCREEN_WIDTH - 50)
        self.rect.y = random.randrange(-200, -100)
        self.used = False

    def update(self):
        self.float()
        if (self.rect.y > data.SCREEN_HEIGHT) or self.used:
            if self.used:
                self.game.up_sound.play()
            self.kill()

    def float(self):
        pygame.time.get_ticks()
        self.rect.y += self.vy
        self.rect.x += self.vx

        if self.rect.x > data.SCREEN_WIDTH or self.rect.x < 0:
            self.vx *= -1
            if self.vx > 0:
                self.image = self.imageLst[0]
            else:
                self.image = self.imageLst[1]


class Cursor:
    def __init__(self, game):
        self.game = game
        self.offset = -75
        self.selected = "PLAY"
        self.image = pygame.image.load("source/PenguinJump/Sprites/cursor.png")
        self.x = data.SCREEN_WIDTH / 2 + self.offset
        self.y = data.SCREEN_HEIGHT * 3 / 4
        self.selectedGO = "PLAY_AGAIN"

    def move_cursor(self, event):
        if event.type == pygame.KEYDOWN:  # better method for keeping track of how many times space is pressed
            if (event.key == self.game.UP_KEY and self.selected == "OPTIONS") or (
                    event.key == self.game.DOWN_KEY and self.selected == "OPTIONS"):
                self.game.select_sound.play()
                self.selected = "PLAY"
                self.x = data.SCREEN_WIDTH / 2 + self.offset
                self.y = data.SCREEN_HEIGHT * 3 / 4
            elif (event.key == self.game.DOWN_KEY and self.selected == "PLAY") or (
                    event.key == self.game.UP_KEY and self.selected == "PLAY"):
                self.game.select_sound.play()
                self.selected = "OPTIONS"
                self.x = data.SCREEN_WIDTH / 2 + self.offset
                self.y = data.SCREEN_HEIGHT * 3 / 4 + 30

    def move_cursor_options(self, event):
        self.offset = -125
        if event.type == pygame.KEYDOWN:
            if event.key == self.game.DOWN_KEY:
                self.game.select_sound.play()
                self.selected = "CONTROLS"
                self.x = data.SCREEN_WIDTH / 2 + self.offset
                self.y = data.SCREEN_HEIGHT / 2 + 30
            elif event.key == self.game.UP_KEY:
                self.game.select_sound.play()
                self.selected = "VOLUME"
                self.x = data.SCREEN_WIDTH / 2 + self.offset
                self.y = data.SCREEN_HEIGHT / 2

    def control_option_cursor(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    return True
                elif event.key == self.game.LEFT_KEY:
                    self.game.select_sound.play()
                    self.selected = "ASDW"
                    self.x = data.SCREEN_WIDTH / 4 + self.offset
                    self.y = data.SCREEN_HEIGHT / 2 + 80
                elif event.key == self.game.RIGHT_KEY:
                    self.game.select_sound.play()
                    self.selected = "ARROWS"
                    self.x = data.SCREEN_WIDTH * 3 / 4 + self.offset - 50
                    self.y = data.SCREEN_HEIGHT / 2 + 80
                elif (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER) and self.selected == "ASDW":
                    self.game.press_sound.play()
                    self.game.LEFT_KEY = pygame.K_a
                    self.game.RIGHT_KEY = pygame.K_d
                    self.game.UP_KEY = pygame.K_w
                    self.game.DOWN_KEY = pygame.K_s
                elif (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER) and self.selected == "ARROWS":
                    self.game.press_sound.play()
                    self.game.LEFT_KEY = pygame.K_LEFT
                    self.game.RIGHT_KEY = pygame.K_RIGHT
                    self.game.UP_KEY = pygame.K_UP
                    self.game.DOWN_KEY = pygame.K_DOWN
            else:
                return False

    def control_option_sound(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    return True
                elif event.key == self.game.LEFT_KEY:
                    self.game.select_sound.play()
                    self.selected = "LOWER"
                    self.x = data.SCREEN_WIDTH / 4 + self.offset
                    self.y = data.SCREEN_HEIGHT / 2 + 80
                elif event.key == self.game.RIGHT_KEY:
                    self.game.select_sound.play()
                    self.selected = "RAISE"
                    self.x = data.SCREEN_WIDTH * 3 / 4 - 50
                    self.y = data.SCREEN_HEIGHT / 2 + 80
                elif (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER) and self.selected == "LOWER":
                    if self.game.VOLUME_SETTING > 0:
                        self.game.VOLUME_SETTING -= 10

                    else:
                        self.game.VOLUME_SETTING = 0
                    self.game.volume_mult = self.game.VOLUME_SETTING / 100

                elif (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER) and self.selected == "RAISE":
                    if self.game.VOLUME_SETTING < 100:
                        self.game.VOLUME_SETTING += 10
                    else:
                        self.game.VOLUME_SETTING = 100
                    self.game.volume_mult = self.game.VOLUME_SETTING / 100

            else:
                return False

    def gameover_cursor(self):
        for event in pygame.event.get():
            self.offset = -175
            if event.type == pygame.QUIT:
                self.game.running = False
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.running = False
                    return False
                if event.key == pygame.K_F5:
                    self.game.fullScreen = not self.game.fullScreen
                    if self.game.fullScreen:
                        self.game.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        self.game.screen = pygame.display.set_mode((data.SCREEN_WIDTH, data.SCREEN_HEIGHT))

                if event.key == self.game.DOWN_KEY:
                    self.game.select_sound.play()
                    self.selectedGO = "RETURN"
                    self.x = data.SCREEN_WIDTH / 2 + self.offset
                    self.y = data.SCREEN_HEIGHT / 2 + 30
                    return False
                elif event.key == self.game.UP_KEY:
                    self.game.select_sound.play()
                    self.selectedGO = "PLAY_AGAIN"
                    self.x = data.SCREEN_WIDTH / 2 + self.offset
                    self.y = data.SCREEN_HEIGHT / 2
                    return False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.game.press_sound.play()
                    return True

    def draw_cursor(self):
        self.game.screen.blit(self.image, (self.x, self.y))


class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert()

    def get_image(self, x, y, w, h):
        # grab the image out of a larger sprite sheet
        image = pygame.Surface((w, h))
        image.set_colorkey(data.black)
        image.blit(self.spritesheet, (0, 0), (x, y, w, h))
        return image
    

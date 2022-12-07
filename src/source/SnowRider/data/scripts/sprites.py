import random

from source.SnowRider.data.scripts.constants import *
from source.SnowRider.data.scripts.draw import draw_text


# Draw radius
# temp_rect = self.image.get_rect()
# pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

class Player(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.image = images
        self.image_orig = images
        self.rect = self.image.get_rect()
        self.rect.centerx = win_res["WEIGHT"] / 2
        self.rect.bottom = win_res["HEIGHT"] + 64
        self.spawn_y = win_res["HEIGHT"] * 0.9
        self.spawned = False
        self.direction = "forward"
        self.has_collided = False
        # For speed
        self.speedx = 0
        self.movspd = 6
        self.speedy = 0
        # For collision
        self.radius = 16

    def update(self):
        if self.spawned:
            if not self.has_collided:
                self.speedx = 0
                self.image = self.image_orig
                
                # Get pressed key
                pressed = pygame.key.get_pressed()

                if pressed[pygame.K_a]:
                    self.speedx = -self.movspd
                    self.rotate_img(40)
                elif pressed[pygame.K_d]:
                    self.speedx = self.movspd
                    self.rotate_img(-40)

                # Draw radius
                # temp_rect = self.image.get_rect()
                # pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

                # Move sprite on the x-axis
                self.rect.x += self.speedx

                self.check_oob()
            else:
                self.rect.y += self.speedy

    def check_oob(self):
        # Check if sprite is out of bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.speedx = 0
        elif self.rect.right > win_res["WEIGHT"]:
            self.rect.right = win_res["WEIGHT"]
            self.speedx = 0

    def rotate_img(self, angle):
        orig_rect = self.image.get_rect()
        rot_image = pygame.transform.rotate(self.image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.image = rot_image


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.palette = list()
        self.image = self.roll_img(images)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, win_res["WEIGHT"] - 64)
        self.rect.y = random.randrange(-1028, -128)
        self.speedy = SPRITE_MOVESPEED
        # For collision
        self.radius = 28

    def update(self):
        # Draw radius
        # temp_rect = self.image.get_rect()
        # pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

        self.rect.y += self.speedy

        if self.rect.top > win_res["HEIGHT"]:
            self.kill()

    def roll_img(self, images): 
        # is the weight for each image in the list,
        # [8, 8, 8, 1, 1, 1, 1, 1] = 25% chance of each image being selected (8/32) * 100 = 25%
        # The function returns a k sized list of population elements chosen with replacement.
        # If the relative weights or cumulative weights are not specified, the selections are made with equal probability.
        img_list = images
        choices = random.choices(img_list, [8, 8, 8, 1, 1, 1, 1, 1], k=10)
        choice = random.choice(choices)

        # Get color information of the surface
        self.palette.append(choice.get_at((32, 32))) # Top left
        self.palette.append(choice.get_at((42, 42))) # Top right
        self.palette.append(choice.get_at((32, 48))) # Bottom left

        # Return choice
        return choice


class Fracture(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.variant = random.choice(["a", "b"])
        self.images = images[self.variant]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(-32, win_res["WEIGHT"] - 64)
        self.rect.y = random.randrange(-512, -128)
        self.speedy = SPRITE_MOVESPEED
        self.fracture_timer = pygame.time.get_ticks()
        self.fracture_delay = random.randrange(250, 500)
        self.fractured = False
        # For animation
        self.frame = 0
        self.frame_timer = pygame.time.get_ticks()
        self.frame_delay = 200
        # For collision
        self.radius = 48

    def update(self):

        # Draw radius
        # temp_rect = self.image.get_rect()
        # pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

        self.rect.y += self.speedy

        now = pygame.time.get_ticks()
        if now - self.fracture_timer > self.fracture_delay:
            self.animate()

        if self.rect.top > win_res["HEIGHT"]:
            self.kill()

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.frame_timer > self.frame_delay and self.frame != len(self.images) - 1:
            old_rectx = self.rect.x
            old_recty = self.rect.y
            self.frame_timer = now
            self.frame += 1
            self.image = self.images[self.frame]
            self.rect = self.image.get_rect()
            self.rect.x = old_rectx
            self.rect.y = old_recty
            if self.frame == 4:
                self.fractured = True


class Debris(pygame.sprite.Sprite):
    def __init__(self, images, window):
        super().__init__()
        self.images = images
        size = random.randrange(200, 232)
        self.img_roll = random.randrange(0, len(images))
        self.image = pygame.transform.scale(self.images["normal"][self.img_roll], (size, size))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(64, win_res["WEIGHT"] - 64)
        self.rect.centery = win_res["HEIGHT"] * 1.2
        self.window = window
        self.impacted = False
        self.img_changed = False
        self.speedy = SPRITE_MOVESPEED
        self.speedx = self.calc_speedx()
        self.shaked = False  # Bool if it has shaked the screen. See game loop.
        self.is_above_player = False
        # The point at which the object will stop moving on the y-axis
        self.max_disty = random.randrange(96, win_res["HEIGHT"] * 0.3)
        # For shrinking
        self.shrink_timer = pygame.time.get_ticks()
        self.shrink_delay = 80
        self.scaler = 0
        # For collision
        self.radius = 64

    def update(self):

        # Draw radius
        # temp_rect = self.image.get_rect()
        # pygame.draw.circle(self.image, (255,0,0), temp_rect.center, self.radius)

        # Stop on the specified y-axis line
        if self.rect.top < self.max_disty:
            self.impacted = True

        if self.impacted:
            self.rect.y += self.speedy
            if not self.img_changed:
                self.change_image()
                self.img_changed = True
                self.radius = self.image.get_width() // 3
        else:
            self.rect.y -= random.randrange(SPRITE_MOVESPEED + 2, SPRITE_MOVESPEED + 5)
            self.rect.x += self.speedx
            self.shrink()

        # Delete sprite if it goes off screen
        if self.impacted and self.rect.top > win_res["HEIGHT"]:
            self.kill()

    def shrink(self):
        now = pygame.time.get_ticks()
        if now - self.shrink_timer > self.shrink_delay:
            old_x = self.rect.centerx
            old_y = self.rect.centery
            self.shrink_timer = now
            x_scale = self.image.get_width() - self.scaler
            y_scale = self.image.get_height() - self.scaler
            self.image = pygame.transform.scale(self.image, (x_scale, y_scale))
            self.rect = self.image.get_rect()
            self.rect.centerx = old_x
            self.rect.centery = old_y
            self.scaler += 1

    def change_image(self):
        old_x = self.rect.centerx
        old_y = self.rect.centery
        x_scale = self.image.get_width() - self.scaler
        y_scale = self.image.get_height() - self.scaler
        self.image = pygame.transform.scale(self.images["impacted"][self.img_roll], (x_scale, y_scale))
        self.rect.centerx = old_x
        self.rect.centery = old_y

    def calc_speedx(self):
        if self.rect.centerx > win_res["WEIGHT"] / 2:
            return random.randrange(-7, -1)
        elif self.rect.centerx < win_res["WEIGHT"] / 2:
            return random.randrange(1, 7)
        else:
            return random.choice([-2, 2])


class Particle:
    def __init__(self, window, win_res, x, y, colors, launch_type, font):
        self.window = window
        self.font = font
        self.win_res = win_res
        self.x = x
        self.y = y
        self.movspd = SPRITE_MOVESPEED
        self.color = random.choice(colors)
        self.launch_type = launch_type
        if self.launch_type == "explosion":
            self.speedx = random.choice([num for num in range(-8, 8) if num not in [-2, -1, 0, 1, 2]])
            self.speedy = random.choice([num for num in range(-6, 6) if num not in [-2, -1, 0, 1, 2]])
            self.size = random.choice([8, 12])
        elif self.launch_type == "trail":
            self.speedx = 0
            self.speedy = SPRITE_MOVESPEED
            self.size = 16
            self.y = self.y - 32
        elif self.launch_type == "coins":
            self.speedx = random.choice([-1, 1])
            self.speedy = -1
            self.size = 16
            self.y = self.y + random.randrange(-16, 16)

    def draw(self):
        self.x += self.speedx
        self.y += self.speedy
        if self.launch_type == "explosion":
            if self.speedx > 0:
                self.speedx -= 0.1
            if self.speedy < self.movspd:
                self.speedy += 0.1
            elif self.speedy > self.movspd:
                self.speedy -= 0.1
            pygame.draw.rect(self.window, self.color, (self.x, self.y, self.size, self.size))
        elif self.launch_type == "trail":
            pygame.draw.rect(self.window, self.color, (self.x - 2, self.y, self.size, self.size))
        elif self.launch_type == "coins":
            draw_text(self.window, f"+8", 32, self.font, self.x, self.y, BLACK, "centered")
            self.speedy += 0.5


class Shadow:
    def __init__(self, window, caster, x, y):
        self.window = window
        self.x = x
        self.y = round(y * 1.5)
        self.Caster = caster

    def draw(self):
        radius = 5 * (self.Caster.scaler + 1)
        pygame.draw.circle(self.window, SHADOW, (self.Caster.rect.centerx, self.y), radius)
        # pygame.draw.circle(self.window, SHADOW, (self.Caster.rect.centerx, self.y), radius)


class Bouncy:
    def __init__(self, window):
        self.window = window
        self.x = random.randrange(0, window.get_width())
        self.y = random.randrange(0, window.get_height())
        self.size = random.choice([16, 32])
        self.speedx = random.choice([-3, 3])
        self.speedy = random.choice([-3, 3])

    def draw(self):

        if self.x < 0:
            self.speedx = abs(self.speedx)
        elif self.x > self.window.get_width():
            self.speedx = -self.speedx

        if self.y < 0:
            self.speedy = abs(self.speedy)
        elif self.y > self.window.get_height():
            self.speedy = -self.speedy

        pygame.draw.rect(self.window, SHADOW, (self.x, self.y, self.size, self.size))

        self.x += self.speedx
        self.y += self.speedy
        

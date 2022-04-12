import pygame
import random

WIDTH, HEIGHT = 900, 500
run = True

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.image.load('assets/Background.png')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
pygame.display.set_caption("Scheleton vs Slimes")

pygame.mixer.music.load("assets/sounds/background_music.mp3")
pygame.mixer.music.set_volume(0.05)

bone_sprites = pygame.sprite.Group()

pointer = pygame.image.load('assets/arrow.png')
pointer_rect = pointer.get_rect()

# Events
START_MENU = pygame.USEREVENT + 1

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PLAYER_MAXIMUM_HEALTH = 5
PLAYER_VEL = 3

clock = pygame.time.Clock()
FPS = 60


class PowerUP(pygame.sprite.Sprite):
    def __init__(self, type, pos_x, pos_y, width, height):
        super().__init__()
        self.move_x = 0
        self.move_y = 0
        self.width = width
        self.height = height
        self.type = type
        self.is_jumping = False
        self.is_falling = True
        self.collided_with_player = False

        self.jump_count = 10

        self.gain_health_sound = pygame.mixer.Sound("assets/sounds/gain_health_sound.mp3")

        if self.type == 'health':
            self.health = []
            self.health.append(pygame.image.load('assets/heart/heart_02.png').convert_alpha())
            self.health.append(pygame.image.load('assets/heart/heart_01.png').convert_alpha())
            self.current_sprite = 0

        self.image = self.health[int(self.current_sprite)]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x, pos_y)

    def check_collision(self, sprite):
        col = pygame.sprite.collide_rect(self, sprite)
        if col:
            if self.rect.y + self.height >= sprite.rect.y:
                self.rect.y = sprite.rect.y - self.height
            self.is_falling = False
            self.move_y = 0
        elif self.is_falling:
            self.move_y += 0.1
        self.rect.y += self.move_y

    def check_player_collision(self, sprite):
        col = pygame.sprite.collide_rect(self, sprite)
        if col and not self.collided_with_player:
            if player.maximum_health == player.health:
                if player.maximum_health < PLAYER_MAXIMUM_HEALTH:
                    player.maximum_health += 1
            if player.maximum_health > player.health:
                player.health += 1
                self.gain_health_sound.set_volume(0.2)
                self.gain_health_sound.play(fade_ms=100)

            self.collided_with_player = True
            # print(player.maximum_health, player.health)
            self.kill()

    def pop_out(self):
        if self.is_jumping:
            if self.jump_count >= 0:
                self.rect.y -= int((self.jump_count**2) * 0.03)
                self.jump_count -= 1
            else:
                self.is_jumping = False
                self.is_falling = True
                self.jump_count = 10

    def update(self):
        self.image = self.health[int(self.current_sprite)]
        self.current_sprite = 1
        if self.current_sprite >= len(self.health):
            self.current_sprite = 0
        for powerup in powerup_sprites:
            if powerup == self:
                if not self.is_falling:
                    self.is_jumping = True
                    powerup.pop_out()


class Health(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.number_of_hearts = 0
        self.x = 5
        self.player_health = 3
        self.player_has_collided = player.collided_with_enemy

        self.hearts = []
        self.hearts.append(pygame.image.load('assets/heart/heart_01.png').convert_alpha())
        self.hearts.append(pygame.image.load('assets/heart/heart_02.png').convert_alpha())
        self.hearts.append(pygame.image.load('assets/heart/heart_03.png').convert_alpha())
        self.current_sprite = 0

        self.image = self.hearts[int(self.current_sprite)]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x, pos_y)

    def update(self):
        self.x = 5
        self.player_health = int(player.health)
        self.player_has_collided = player.collided_with_enemy
        player_maximum_health = player.maximum_health
        for i in range(player_maximum_health):
            if i < self.player_health:
                self.image = self.hearts[0]
                WIN.blit(self.image, (self.x + 5, 10))
            else:
                self.image = self.hearts[2]
                WIN.blit(self.image, (self.x + 5, 10))

            self.x += 17


class Level(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.move_x = 0
        self.move_y = 0
        self.width = width
        self.height = height
        self.color = WHITE
        self.image = pygame.image.load('assets/ground.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x, pos_y)

    def render(self):
        pygame.draw.rect(WIN, self.color, pygame.Rect(self.rect.x, self.rect.y, self.width, self.height))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, color, pos_x, pos_y, width, height):
        super().__init__()
        self.move_x = 0
        self.move_y = 0
        self.width = width
        self.height = height
        self.color = color
        self.player_inactivity_timer = 10000  # 10 seconds (1000 ticks per second)

        self.jump_count = 10
        self.is_jumping = False
        self.is_falling = True
        self.able_to_collide = True

        self.change_side = False
        self.moved_to = False

        self.is_image_flipped = False
        self.is_idle = True
        self.is_running = False
        self.is_dying = False

        self.hit_ground_sound = pygame.mixer.Sound("assets/sounds/slime_hit_ground.mp3")
        self.die_sound = pygame.mixer.Sound("assets/sounds/slime_die.mp3")

        if self.color == 'yellow':
            self.idle = []
            self.idle.append(pygame.image.load('assets/slime/yellow/idle_01.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/yellow/idle_02.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/yellow/idle_03.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/yellow/idle_04.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/yellow/idle_05.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/yellow/idle_06.png').convert_alpha())

            self.jump = []
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_01.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_02.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_03.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_04.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_05.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_06.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_07.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_08.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/yellow/jump_09.png').convert_alpha())

            self.die = []
            self.die.append(pygame.image.load('assets/slime/yellow/die_01.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/yellow/die_02.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/yellow/die_03.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/yellow/die_04.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/yellow/die_05.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/yellow/die_06.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/yellow/die_07.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/yellow/die_08.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/yellow/die_09.png').convert_alpha())
        elif self.color == 'red':
            self.idle = []
            self.idle.append(pygame.image.load('assets/slime/red/idle_01.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/red/idle_02.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/red/idle_03.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/red/idle_04.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/red/idle_05.png').convert_alpha())
            self.idle.append(pygame.image.load('assets/slime/red/idle_06.png').convert_alpha())

            self.jump = []
            self.jump.append(pygame.image.load('assets/slime/red/jump_01.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/red/jump_02.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/red/jump_03.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/red/jump_04.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/red/jump_05.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/red/jump_06.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/red/jump_07.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/red/jump_08.png').convert_alpha())
            self.jump.append(pygame.image.load('assets/slime/red/jump_09.png').convert_alpha())

            self.die = []
            self.die.append(pygame.image.load('assets/slime/red/die_01.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/red/die_02.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/red/die_03.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/red/die_04.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/red/die_05.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/red/die_06.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/red/die_07.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/red/die_08.png').convert_alpha())
            self.die.append(pygame.image.load('assets/slime/red/die_09.png').convert_alpha())

        self.current_sprite = 0
        self.current_sprite_dying = 0

        self.image = self.idle[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x, pos_y)

    def move_to(self, pos_x, vel):
        if not self.moved_to and not self.is_dying:
            self.move_x = vel
            if pos_x == self.rect.x:
                self.moved_to = True
                self.is_jumping = True
            elif pos_x < self.rect.x:
                self.move_x *= -1
        else:
            self.move_x = 0

        self.rect.x += self.move_x

    def slime_jump(self):
        if self.is_jumping:
            if self.jump_count >= 0:
                self.rect.y -= int((self.jump_count**2) * 0.2)
                self.jump_count -= 1
            else:
                self.is_jumping = False
                self.is_falling = True
                self.jump_count = 10
                self.moved_to = False

    def check_collision(self, sprite):
        col = pygame.sprite.collide_rect(self, sprite)
        if col:
            if self.rect.y + self.height >= sprite.rect.y:
                self.rect.y = sprite.rect.y - self.height
            self.is_falling = False

            if not self.is_dying:
                self.hit_ground_sound.set_volume(0.1)
                self.hit_ground_sound.play()

            self.move_y = 0
        elif self.is_falling:
            self.move_y += 0.3

    def check_bone_collision(self, sprite):
        col = pygame.sprite.collide_rect(self, sprite)
        if col and not self.is_dying:
            self.able_to_collide = False
            self.is_dying = True
            self.is_running = False
            self.is_jumping = False
            self.is_idle = False
            self.die_sound.set_volume(0.3)
            self.die_sound.play()
            return True
        else:
            return False

    def check_player_collision(self):
        col = pygame.sprite.collide_rect(self, player)
        if player.rect.y + 2 <= self.rect.y and player.is_falling:
            if col:
                self.is_dying = True
                self.die_sound.set_volume(0.3)
                self.die_sound.play()

    def spawn(self):
        if self.rect.y > 500:
            self.rect.x = 200
            self.rect.y = 200

    def update(self):
        if self.move_x > 0:
            self.is_idle = False
            self.is_running = True
            self.is_image_flipped = True
            self.image = pygame.transform.flip(self.jump[int(self.current_sprite)], True, False)
        elif self.move_x < 0:
            self.is_idle = False
            self.is_running = True
            self.is_image_flipped = False
            self.image = self.jump[int(self.current_sprite)]
        elif self.move_x == 0:
            self.is_idle = True
            self.is_running = False

        # Idle and Jumping/Running animations movement
        if self.is_dying:
            if self.is_image_flipped:
                self.image = pygame.transform.flip(self.die[int(self.current_sprite_dying)], True, False)
            else:
                self.image = self.die[int(self.current_sprite_dying)]
            self.current_sprite_dying += 0.2
            if self.current_sprite_dying >= len(self.die):

                if player.enemies_killed > 29:
                    random_x = random.randint(0, 800)
                    random_y = random.randint(0, 400)
                    to_the_left = random_x - player.rect.x
                    x = pygame.time.get_ticks() - self.player_inactivity_timer
                else:
                    random_x = random.randint(0, 800)
                    random_y = random.randint(0, 400)
                    to_the_left = random_x - player.rect.x
                    x = -1
                if x >= player.idle_time:
                    random_x = player.rect.x
                    random_y = 50
                elif 0 <= to_the_left <= 50:
                    if player.rect.x < WIDTH - 82 - 32:
                        random_x += (50 - to_the_left + 32)
                    else:
                        random_x -= (50 + to_the_left + 32)
                elif 0 >= to_the_left >= -50:
                    if player.rect.x > 82:
                        random_x -= (50 + to_the_left + 32)
                    else:
                        random_x += (50 - to_the_left + 32)

                if self.color == 'yellow' and not player.enemies_killed == 20:
                    new_enemy_yellow = Enemy('yellow', random_x, random_y, 32, 32)
                    enemy_sprites.add(new_enemy_yellow)
                elif self.color == 'red':

                    if player.health == 1:
                        spawn_health_or_not = random.randint(0, 1)  # 50% chance
                    else:
                        spawn_health_or_not = random.randint(0, 3)  # 25% chance
                    len_powerup_sprites = 0
                    for _ in powerup_sprites:
                        len_powerup_sprites += 1
                    if not spawn_health_or_not \
                            and not player.maximum_health == player.health \
                            and len_powerup_sprites + player.health <= player.maximum_health:
                        powerup_health = PowerUP('health', self.rect.x + 8, self.rect.y + 8, 16, 16)
                        powerup_sprites.add(powerup_health)
                    new_enemy_red = Enemy('red', random_x, random_y, 32, 32)
                    enemy_sprites.add(new_enemy_red)

                player.enemies_killed += 1
                spawn_enemies()
                self.kill()
        elif self.is_idle:
            self.current_sprite += 0.2
            if self.current_sprite >= len(self.idle):
                self.current_sprite = 0
            if self.is_image_flipped:
                self.image = pygame.transform.flip(self.idle[int(self.current_sprite)], True, False)
            else:
                self.image = self.idle[int(self.current_sprite)]
        elif self.is_running:
            if self.is_image_flipped:
                self.image = pygame.transform.flip(self.jump[int(self.current_sprite)], True, False)
            else:
                self.image = self.jump[int(self.current_sprite)]
            self.current_sprite += 0.2
            if self.current_sprite >= len(self.jump):
                self.current_sprite = 0

        # self.rect.x += self.move_x
        self.rect.y += self.move_y

        if not self.is_falling:
            for enemy in enemy_sprites:
                if enemy == self:
                    if abs(player.rect.x - self.rect.x) <= 500 and self.color == 'yellow':
                        enemy.move_to(player.rect.x, 1)
                    elif self.color == 'red':
                        enemy.move_to(player.rect.x, 1)
                    else:
                        self.move_x = 0


class EnemyFlyer(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__()
        self.move_x = 0
        self.move_y = 0
        self.width = width
        self.height = height
        self.is_idle = True
        self.is_running = False
        self.is_dying = False
        self.is_attacking = False
        self.moved_to = False
        self.is_image_flipped = False
        self.fire_ball_spawned = False
        self.attacked_at = 0
        self.attack_interval_time = random.randint(2000, 9000)  # 2-9 seconds

        self.flyer_bullet_sound = pygame.mixer.Sound("assets/sounds/spawn_flyer_bullet.mp3")

        self.able_to_hover = True
        self.hover_count = 10

        self.fly = []
        for i in range(1, 7):
            frame = pygame.image.load(f"assets/flyer/fly_0{i}.png").convert_alpha()
            frame = pygame.transform.scale(frame, (48, 48))
            self.fly.append(frame)

        self.attack = []
        for i in range(1, 8):
            frame = pygame.image.load(f"assets/flyer/attack_0{i}.png").convert_alpha()
            frame = pygame.transform.scale(frame, (48, 48))
            self.attack.append(frame)
        self.current_sprite = 0
        self.current_sprite_attack = 0
        # self.current_sprite_dying = 0

        self.image = self.fly[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x, pos_y)

    def hover(self):
        if self.able_to_hover:
            if self.hover_count > 0:
                self.rect.y += 1
                self.hover_count -= 1
            elif self.hover_count > -10:
                self.rect.y -= 1
                self.hover_count -= 1
            else:
                self.hover_count = 10
        else:
            self.hover_count = -11

    def move_to(self, pos_x, vel):
        if not self.moved_to and not self.is_dying:
            self.move_x = vel
            if pos_x == self.rect.x:
                self.moved_to = True
                if not self.fire_ball_spawned:
                    self.is_attacking = True
                self.attacked_at = pygame.time.get_ticks()
            elif pos_x < self.rect.x:
                self.move_x *= -1
                self.moved_to = False
                self.is_attacking = False
        else:
            self.move_x = 0

        self.rect.x += self.move_x

    def update(self):
        if self.move_x < 0:
            self.is_idle = False
            self.is_running = True
            self.is_image_flipped = True
            self.image = pygame.transform.flip(self.fly[int(self.current_sprite)], True, False)
        elif self.move_x > 0:
            self.is_idle = False
            self.is_running = True
            self.is_image_flipped = False
            self.image = self.fly[int(self.current_sprite)]
        elif self.move_x == 0:
            self.is_idle = True
            self.is_running = False
            self.able_to_hover = True

        # Idle and Jumping/Running animations movement
        if self.is_attacking:
            if not self.is_image_flipped:
                self.image = pygame.transform.flip(self.attack[int(self.current_sprite_attack)], True, False)
            else:
                self.image = self.attack[int(self.current_sprite_attack)]

            self.current_sprite_attack += 0.1
            if int(self.current_sprite_attack) == 2 and not self.fire_ball_spawned:
                for enemy in enemy_flyer_sprites:
                    if enemy == self:
                        self.flyer_bullet_sound.set_volume(0.2)
                        self.flyer_bullet_sound.play()
                        new_fire_ball = FireBall(enemy.rect.x, enemy.rect.y, 48, 48)
                        fire_ball_sprites.add(new_fire_ball)
                self.fire_ball_spawned = True
            if self.current_sprite_attack >= len(self.attack):
                self.current_sprite_attack = 0
                self.is_attacking = False

        elif self.is_idle or self.is_running:
            if self.is_image_flipped:
                self.image = pygame.transform.flip(self.fly[int(self.current_sprite)], True, False)
            else:
                self.image = self.fly[int(self.current_sprite)]
            self.current_sprite += 0.3
            if self.current_sprite >= len(self.fly):
                self.current_sprite = 0

        for flyer in enemy_flyer_sprites:
            if flyer == self:
                flyer.move_to(player.rect.x, 1)
                flyer.hover()

        # time in between each attack
        x = pygame.time.get_ticks() - self.attack_interval_time
        if x >= self.attacked_at:
            self.moved_to = False
            self.fire_ball_spawned = False
        # print(x, self.attacked_at, self.moved_to)
        # self.rect.y += self.move_y


class FireBall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__()
        self.move_x = 0
        self.move_y = 0
        self.width = width
        self.height = height
        self.hit_the_ground = False

        self.explosion_sound = pygame.mixer.Sound("assets/sounds/explosion_sound.mp3")

        self.fire_ball = pygame.image.load("assets/flyer/attack_03.png")
        self.fire_ball = pygame.transform.scale(self.fire_ball, (48, 48))

        self.explosion = []
        for i in range(1, 9):
            frame = pygame.image.load(f"assets/explosion/explosion_0{i}.png").convert_alpha()
            frame = pygame.transform.scale(frame, (96, 96))
            self.explosion.append(frame)
        for i in range(10, 11):
            frame = pygame.image.load(f"assets/explosion/explosion_{i}.png").convert_alpha()
            frame = pygame.transform.scale(frame, (96, 96))
            self.explosion.append(frame)
        self.current_sprite = 0

        self.image = self.fire_ball
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x, pos_y)

    def update(self):
        if self.move_y <= 8:
            self.move_y += 0.1
        else:
            self.move_y = 8

        if self.rect.y >= 420:
            self.hit_the_ground = True
            self.explosion_sound.set_volume(0.07)
            self.explosion_sound.play()
            self.rect.x -= 24

        if self.hit_the_ground:
            self.rect.y = 396
            self.move_y = 0
            self.image = self.explosion[int(self.current_sprite)]
            self.current_sprite += 0.2
            if self.current_sprite >= len(self.explosion):
                self.current_sprite = 0
                self.kill()
        self.rect.y += int(self.move_y)


class Bone(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__()
        self.mouse_pos_x, self.mouse_pos_y = pygame.mouse.get_pos()
        self.player_x = player.rect.x + player.width/2
        self.player_y = player.rect.y + player.height/2

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.move_x = 0
        self.move_y = 0
        self.width = width
        self.height = height
        self.BONE_VEL = 13

        self.bones = []
        self.bones.append(pygame.image.load("assets/bone/bone_01.png").convert_alpha())
        self.bones.append(pygame.image.load("assets/bone/bone_02.png").convert_alpha())
        self.bones.append(pygame.image.load("assets/bone/bone_03.png").convert_alpha())
        self.bones.append(pygame.image.load("assets/bone/bone_04.png").convert_alpha())

        self.current_sprite = 0
        self.image = self.bones[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x, pos_y)

    def update(self):
        self.current_sprite += 0.6
        if self.current_sprite >= len(self.bones):
            self.current_sprite = 0

        if self.mouse_pos_x < self.player_x:
            player.is_flipped = False
            self.rect.x -= self.BONE_VEL
            self.image = pygame.transform.flip(self.bones[int(self.current_sprite)], True, False)
        else:
            player.is_flipped = True
            self.rect.x += self.BONE_VEL
            self.image = self.bones[int(self.current_sprite)]

        if not 0 - self.width <= self.rect.x <= WIDTH:
            for _ in bone_sprites:
                bone_sprites.remove(self)
        # print(bone_sprites.sprites())

    def handle_bone_bullets(self):
        if not self.mouse_pos_x < self.player_x:
            self.rect.x = player.rect.x + player.width/2
        else:
            self.rect.x = player.rect.x
        self.rect.y = player.rect.y + player.height/2


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__()
        self.move_x = 0
        self.move_y = 0
        self.width = width
        self.height = height

        self.health = 1
        self.maximum_health = 3
        self.collided_with_enemy = False
        self.idle_time = 0
        self.already_idle = False

        self.invincible = False
        self.invincibility_timer = 2000

        self.jump_count = 10
        self.is_jumping = False
        self.is_falling = True
        self.collided_with_floor = False

        self.enemies_killed = 0
        self.font = pygame.font.Font('assets/fonts/DisposableDroidBB.ttf', 24)
        self.score = self.font.render('Kills: ' + str(self.enemies_killed), True, BLACK)
        self.score_rect = self.score.get_rect()
        self.score_rect.topright = (WIDTH - 20, 10)

        self.highest_score = self.font.render('Highest Kills: ' + str(self.enemies_killed), True, BLACK)
        self.highest_score_value = 0
        self.highest_score_rect = self.highest_score.get_rect()
        self.highest_score_rect.topright = (self.score_rect.topleft[0] - 20, 10)

        self.bones_available = 1
        self.bone_count = pygame.image.load("assets/bone/bone_count.png").convert_alpha()
        self.bone_count_rect = self.bone_count.get_rect()
        self.bone_count_rect.center = (WIDTH / 2 - 320, 20)
        self.bone_count_text = self.font.render('x' + str(self.bones_available), True, BLACK)
        self.bone_count_text_rect = self.bone_count_text.get_rect()
        self.bone_count_text_rect.center = (WIDTH / 2 - 298, 22)

        self.lose_health_sound = pygame.mixer.Sound("assets/sounds/player_lose_health_sound.mp3")
        self.die_sound = pygame.mixer.Sound("assets/sounds/player_die_sound.mp3")
        self.bone_throw_sound = pygame.mixer.Sound("assets/sounds/player_bone_throw.mp3")
        self.hit_ground_sound = pygame.mixer.Sound("assets/sounds/player_hit_ground_sound.mp3")

        self.is_flipped = False
        self.is_idle = True
        self.idle = []
        self.idle.append(pygame.image.load('assets/scheleton/idle_01.png').convert_alpha())
        self.idle.append(pygame.image.load('assets/scheleton/idle_02.png').convert_alpha())
        self.idle.append(pygame.image.load('assets/scheleton/idle_03.png').convert_alpha())
        self.idle.append(pygame.image.load('assets/scheleton/idle_04.png').convert_alpha())
        self.idle.append(pygame.image.load('assets/scheleton/idle_05.png').convert_alpha())
        self.idle.append(pygame.image.load('assets/scheleton/idle_06.png').convert_alpha())

        self.is_running = False
        self.run = []
        self.run.append(pygame.image.load('assets/scheleton/run_01.png').convert_alpha())
        self.run.append(pygame.image.load('assets/scheleton/run_02.png').convert_alpha())
        self.run.append(pygame.image.load('assets/scheleton/run_03.png').convert_alpha())
        self.run.append(pygame.image.load('assets/scheleton/run_04.png').convert_alpha())
        self.run.append(pygame.image.load('assets/scheleton/run_05.png').convert_alpha())
        self.run.append(pygame.image.load('assets/scheleton/run_06.png').convert_alpha())
        self.run.append(pygame.image.load('assets/scheleton/run_07.png').convert_alpha())
        self.run.append(pygame.image.load('assets/scheleton/run_08.png').convert_alpha())

        self.jump_up = []
        self.jump_up.append(pygame.image.load('assets/scheleton/jump_01.png').convert_alpha())
        self.jump_up.append(pygame.image.load('assets/scheleton/jump_02.png').convert_alpha())

        self.is_dying = False
        self.die = []
        self.die.append(pygame.image.load('assets/scheleton/die_01.png').convert_alpha())
        self.die.append(pygame.image.load('assets/scheleton/die_02.png').convert_alpha())
        self.die.append(pygame.image.load('assets/scheleton/die_03.png').convert_alpha())
        self.die.append(pygame.image.load('assets/scheleton/die_04.png').convert_alpha())
        self.die.append(pygame.image.load('assets/scheleton/die_05.png').convert_alpha())
        self.die.append(pygame.image.load('assets/scheleton/die_06.png').convert_alpha())
        self.die.append(pygame.image.load('assets/scheleton/die_07.png').convert_alpha())
        self.die.append(pygame.image.load('assets/scheleton/die_08.png').convert_alpha())
        self.dying_current_sprite = 0
        self.current_sprite = 0

        self.current_sprite_collided = 0
        self.start_collision_animation = False
        self.collided_at_time = 0
        self.brighten = 128

        self.image = self.idle[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x, pos_y)

    def control(self, pos_x):
        self.move_x += pos_x

    def move(self):
        self.rect.x += self.move_x
        self.move_x = 0
        self.rect.y += self.move_y

    def jump(self):
        if self.is_jumping:
            if self.jump_count >= 0:
                self.rect.y -= int((self.jump_count**2) * 0.3)
                self.jump_count -= 1
            else:
                self.is_jumping = False
                self.is_falling = True
                self.jump_count = 10

    def check_collision(self, sprite):
        col = pygame.sprite.collide_rect(self, sprite)
        if col and not self.collided_with_floor:
            if self.rect.y + self.height >= sprite.rect.y:
                self.rect.y = sprite.rect.y - self.height
            self.is_falling = False
            self.move_y = 0
            self.collided_with_floor = True
            self.hit_ground_sound.set_volume(0.1)
            self.hit_ground_sound.play(fade_ms=150)
        elif self.is_falling:
            self.move_y += 0.6
            self.collided_with_floor = False

    def check_enemy_collision(self, sprite):
        col = pygame.sprite.collide_rect(self, sprite)
        if not self.rect.y + 16 <= sprite.rect.y \
                and not self.is_falling:
            if col:
                if not self.collided_with_enemy and not self.invincible:
                    self.collided_at_time = pygame.time.get_ticks()
                    self.start_collision_animation = True
                    self.invincible = True
                    self.collided_with_enemy = True
                    self.health -= 1
                    if self.health > 0:
                        self.lose_health_sound.set_volume(0.2)
                        self.lose_health_sound.play()
                    else:
                        self.die_sound.set_volume(0.2)
                        self.die_sound.play()
            else:
                self.collided_with_enemy = False

    def respawn(self):
        if self.health <= 0:
            self.rect.x = 200
            self.rect.y = 200
            self.is_falling = True
            self.collided_with_floor = False
            # self.start_collision_animation = False
            self.health = 1
            self.enemies_killed = 0
            self.bones_available = 1
            pygame.mixer.music.play(-1)
            enemy_sprites.empty()
            powerup_sprites.empty()
            fire_ball_sprites.empty()
            enemy_flyer_sprites.empty()
            first_enemy_yellow = Enemy('yellow', 600, 200, 32, 32)
            enemy_sprites.add(first_enemy_yellow)

    def update(self):
        if self.move_x > 0:
            self.is_idle = False
            self.is_running = True
            self.is_flipped = True
            self.already_idle = False
            self.image = pygame.transform.flip(self.run[int(self.current_sprite)], True, False)
        elif self.move_x < 0:
            self.is_idle = False
            self.is_running = True
            self.is_flipped = False
            self.already_idle = False
            self.image = self.run[int(self.current_sprite)]
        else:
            self.is_idle = True
            self.is_running = False
            if not player.already_idle and self.enemies_killed > 29:
                self.idle_time = pygame.time.get_ticks()
                # print(self.idle_time)
                player.already_idle = True

        if self.health == 0:
            self.is_dying = True

        # Idle and running animations movement
        if self.is_dying and not self.is_falling:
            self.move_x = 0
            self.is_jumping = False
            if self.is_flipped:
                self.image = pygame.transform.flip(self.die[int(self.dying_current_sprite)], True, False)
                self.dying_current_sprite += 0.15
            else:
                self.image = self.die[int(self.dying_current_sprite)]
                self.dying_current_sprite += 0.15
            if self.dying_current_sprite >= len(self.die):
                self.dying_current_sprite = 0
                self.is_dying = False
                player.respawn()
        elif self.is_jumping:
            if self.is_flipped:
                self.image = pygame.transform.flip(self.jump_up[0], True, False)
            else:
                self.image = self.jump_up[0]
        elif self.is_falling:
            if self.is_flipped:
                self.image = pygame.transform.flip(self.jump_up[1], True, False)
            else:
                self.image = self.jump_up[1]
        elif self.is_idle:
            self.current_sprite += 0.2
            if self.current_sprite >= len(self.idle):
                self.current_sprite = 0
            if self.is_flipped:
                self.image = pygame.transform.flip(self.idle[int(self.current_sprite)], True, False)
            else:
                self.image = self.idle[int(self.current_sprite)]
        elif self.is_running:
            self.current_sprite += 0.2
            if self.current_sprite >= len(self.run):
                self.current_sprite = 0

        if self.start_collision_animation and not self.is_dying:
            if self.current_sprite % 1:
                frame = self.image.convert_alpha()
                frame.fill((self.brighten, self.brighten, self.brighten), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = frame
            x = pygame.time.get_ticks() - self.invincibility_timer
            if x >= self.collided_at_time:
                self.start_collision_animation = False
                self.invincible = False

        self.score = self.font.render('Kills: ' + str(self.enemies_killed), True, BLACK)
        self.score_rect = self.score.get_rect()
        self.score_rect.topright = (WIDTH - 20, 10)

        if self.highest_score_value < self.enemies_killed:
            self.highest_score_value = self.enemies_killed
        if self.highest_score_value and not self.highest_score_value == self.enemies_killed:
            self.highest_score = self.font.render('Highest Kills: ' + str(self.highest_score_value), True, BLACK)
            self.highest_score_rect = self.highest_score.get_rect()
            self.highest_score_rect.topright = (self.score_rect.topleft[0] - 20, 10)
            WIN.blit(self.highest_score, self.highest_score_rect)
        WIN.blit(self.score, self.score_rect)

        WIN.blit(self.bone_count, self.bone_count_rect)
        self.bone_count_text = self.font.render('x ' + str(self.bones_available), True, BLACK)
        WIN.blit(self.bone_count_text, self.bone_count_text_rect)


def initiate_hearts():
    x = 5
    health = int(player.health)
    for i in range(health):
        heart = Health(x + 5, 10, 16, 16)
        x += 17
        heart_sprites.add(heart)


def spawn_enemies():
    random_x = random.randint(0, 850)
    random_y = random.randint(0, 400)
    to_the_left = random_x - player.rect.x
    if 0 <= to_the_left <= 50:
        if player.rect.x < WIDTH - 82 - 32:
            random_x += (50 - to_the_left + 32)
        else:
            random_x -= (50 + to_the_left + 32)
    elif 0 >= to_the_left >= -50:
        if player.rect.x > 82:
            random_x -= (50 + to_the_left + 32)
        else:
            random_x += (50 - to_the_left + 32)

    if player.enemies_killed == 10:
        new_enemy_yellow = Enemy('yellow', random_x, random_y, 32, 32)
        enemy_sprites.add(new_enemy_yellow)
    elif player.enemies_killed == 20:
        new_enemy_red = Enemy('red', random_x, random_y, 32, 32)
        enemy_sprites.add(new_enemy_red)
    elif player.enemies_killed == 50:
        player.bones_available += 1
        enemy_flyer = EnemyFlyer(900, 60, 48, 48)
        enemy_flyer_sprites.add(enemy_flyer)
    elif player.enemies_killed == 120:
        new_enemy_red = Enemy('red', random_x, random_y, 32, 32)
        enemy_sprites.add(new_enemy_red)
    elif player.enemies_killed == 150:
        enemy_flyer = EnemyFlyer(-48, 100, 48, 48)
        enemy_flyer_sprites.add(enemy_flyer)
    elif not player.enemies_killed % 100:
        new_enemy_red = Enemy('red', random_x, random_y, 32, 32)
        enemy_sprites.add(new_enemy_red)
    if not player.enemies_killed % 200:
        player.bones_available += 1


def draw_window():
    WIN.blit(background, (0, 0))
    player_sprites.draw(WIN)
    player_sprites.update()
    player.check_collision(floor)
    player.jump()
    player.move()
    for fire_ball in fire_ball_sprites:
        player.check_enemy_collision(fire_ball)

    enemy_sprites.draw(WIN)
    enemy_sprites.update()
    for enemies in enemy_sprites:
        if not enemies.is_dying:
            player.check_enemy_collision(enemies)
            enemies.check_player_collision()
        enemies.check_collision(floor)
        enemies.slime_jump()
        for bullet in bone_sprites:
            if enemies.check_bone_collision(bullet):
                bone_sprites.remove(bullet)

    enemy_flyer_sprites.draw(WIN)
    enemy_flyer_sprites.update()

    powerup_sprites.draw(WIN)
    powerup_sprites.update()
    for powerup in powerup_sprites:
        powerup.check_collision(floor)
        powerup.check_player_collision(player)

    heart_sprites.update()
    bone_sprites.draw(WIN)
    bone_sprites.update()

    fire_ball_sprites.draw(WIN)
    fire_ball_sprites.update()

    # changing the mouse pointer
    pointer_rect.center = pygame.mouse.get_pos()
    mouse_x, _ = pygame.mouse.get_pos()
    if mouse_x > player.rect.x + player.width/2:
        pointer_flipped = pygame.transform.flip(pointer, True, False)
        WIN.blit(pointer_flipped, pointer_rect)
    else:
        WIN.blit(pointer, pointer_rect)

    # floor.render()
    pygame.display.flip()  # pygame.display.update()


def paused(pause):
    font = pygame.font.Font('assets/fonts/DisposableDroidBB.ttf', 96)
    pause_text = font.render('Paused', True, WHITE)
    pause_text_rect = pause_text.get_rect()
    pause_text_rect.center = ((WIDTH / 2), (HEIGHT / 2 - 35))

    font_2 = pygame.font.Font('assets/fonts/DisposableDroidBB.ttf', 56)
    reset_text = font_2.render('Press R to Restart', True, WHITE)
    reset_text_rect = reset_text.get_rect()
    reset_text_rect.center = ((WIDTH/2), (HEIGHT/2 + 35))

    darken = 110
    WIN.fill((darken, darken, darken), special_flags=pygame.BLEND_RGBA_MULT)
    pygame.mouse.set_visible(True)
    pygame.mixer.music.stop()
    while pause:
        WIN.blit(pause_text, pause_text_rect)
        WIN.blit(reset_text, reset_text_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pause = False
                global run
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    pause = False
                    pygame.mixer.music.play(-1)
                if event.key == pygame.K_r:
                    pause = False
                    player.health = 0
                    player.respawn()
        pygame.display.update()
        clock.tick(15)
    pygame.mouse.set_visible(False)


def start_page(start):
    intro_background = pygame.image.load('assets/intro_background.jpg')
    intro_background = pygame.transform.scale(intro_background, (WIDTH, HEIGHT))

    font = pygame.font.Font('assets/fonts/DisposableDroidBB.ttf', 56)
    start_text = font.render('START GAME', False, WHITE)
    start_text_rect = start_text.get_rect()
    start_text_rect.center = ((WIDTH / 2), (HEIGHT / 2))

    font_2 = pygame.font.Font('assets/fonts/DisposableDroidBB.ttf', 24)
    credit_text = font_2.render('Made by EMi', False, WHITE)
    credit_text_rect = credit_text.get_rect()
    credit_text_rect.bottomright = ((WIDTH - 20), (HEIGHT - 10))

    pygame.mouse.set_visible(True)

    while start:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
                global run
                run = False
            if event.type == pygame.MOUSEBUTTONUP and start_text_rect.collidepoint(mouse_pos):
                start = False
                pygame.mixer.music.play(-1)

        WIN.blit(intro_background, (0, 0))
        if start_text_rect.collidepoint(mouse_pos):
            pygame.draw.rect(WIN, '#0C163C', start_text_rect)
            pygame.draw.rect(WIN, '#0C163C', start_text_rect, 15)
        WIN.blit(start_text, start_text_rect)
        WIN.blit(credit_text, credit_text_rect)
        clock.tick(15)
        pygame.display.update()
    pygame.mouse.set_visible(False)


def main():
    global run
    run = True
    start_page_event = pygame.event.Event(START_MENU)
    pygame.event.post(start_page_event)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == START_MENU:
                start_page(True)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.is_falling:
                    player.is_jumping = True
                if (event.key == pygame.K_p or event.key == pygame.K_ESCAPE) and not player.is_dying:
                    paused(True)
            if event.type == pygame.MOUSEBUTTONUP:
                if len(bone_sprites) < player.bones_available and not player.is_dying:
                    player.bone_throw_sound.set_volume(0.08)
                    player.bone_throw_sound.play(fade_ms=150)
                    bone = Bone(200, 200, 16, 16)
                    bone_sprites.add(bone)
                    bone.handle_bone_bullets()
                    ran_num = random.randint(0, 2)
                    for enemy in enemy_sprites:
                        if ran_num and not enemy.is_falling and enemy.color == 'red' and not enemy.is_dying:
                            if abs(player.rect.x - enemy.rect.x) <= 400:
                                enemy.is_jumping = True
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_LSHIFT]:
            PLAYER_VEL = 5
        else:
            PLAYER_VEL = 3
        if key_pressed[pygame.K_a]:  # Left
            if player.rect.x > 0:
                player.control(-PLAYER_VEL)
        if key_pressed[pygame.K_d]:  # Right
            if player.rect.x + player.width < WIDTH:
                player.control(PLAYER_VEL)

        clock.tick(FPS)
        draw_window()

    pygame.quit()


if __name__ == "__main__":
    player_sprites = pygame.sprite.Group()
    player = Player(200, 200, 32, 32)
    player_sprites.add(player)

    enemy_sprites = pygame.sprite.Group()
    enemy_yellow = Enemy('yellow', 600, 200, 32, 32)
    enemy_sprites.add(enemy_yellow)

    enemy_flyer_sprites = pygame.sprite.Group()

    powerup_sprites = pygame.sprite.Group()

    heart_sprites = pygame.sprite.Group()
    initiate_hearts()

    fire_ball_sprites = pygame.sprite.Group()

    floor = Level(0, 460, 900, 40)

    main()

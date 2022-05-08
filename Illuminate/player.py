import pygame
import math
from settings import *
from pygame.math import Vector2
from audio_sfx_player import SFX
from random import randint, choice



class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)

        #Audio Information
        self.sfx = SFX(['Audio/SFX/Player'], [".wav"])
        self.landSoundCheck = False
        self.idleTimer = 0
        self.idleSounds = ["001_breathing1.wav", "001_breathing2.wav", "001_breathing3.wav", "001_breathing4.wav"]
        self.sfx.setVolume("001_breathing1.wav", .1)
        self.sfx.setVolume("004_jump.wav", .3)
        self.sfx.setVolume("001_grunt_placeholder.wav", 1.2)

        #Game Referneces
        self.game = game

        #Animation Information
        self.player_image = pygame.image.load("image.png")
        self.player_image.set_colorkey((14, 209, 69))
        self.image_width = self.player_image.get_width() // 8
        self.image_height = self.player_image.get_height() // 2
        self.image = pygame.Surface((self.image_width, self.image_height))
        self.image.set_colorkey((0,0,0))
        self.image.blit(self.player_image, (0, 0), (0, 0, self.image_width, self.image_height))
        pygame.draw.rect(self.image, (255, 0, 0), self.image.get_rect(), 1)
        # self.image.fill(PLAYERCOLOR)
        self.flipped = False
        self.current_frame = 0
        self.stateTime = 0
        self.current_anim = "idle"
        self.animations = {"walking": [(0, 0, self.image_width, self.image_height),
                                       (self.image_width, 0, self.image_width, self.image_height),
                                       (self.image_width * 2, 0, self.image_width, self.image_height),
                                       (self.image_width * 3, 0, self.image_width, self.image_height),
                                       (self.image_width * 4, 0, self.image_width, self.image_height),
                                       (self.image_width * 5, 0, self.image_width, self.image_height),
                                       (self.image_width * 6, 0, self.image_width, self.image_height),
                                       (self.image_width * 7, 0, self.image_width, self.image_height)],
                           "idle": [(self.image_width, self.image_height, self.image_width, self.image_height)],
                           "jumping": [(0, self.image_height, self.image_width, self.image_height)],
                           "jumping_left": [
                                  (self.image_width * 7, self.image_height, self.image_width, self.image_height)],
                           "sliding": [
                                  (self.image_width * 2, self.image_height, self.image_width, self.image_height)]}
        self.anime_timer = 0
        self.slide_timer = 2
        self.length_timer = .3


        #Physics Information
        self.grounded = False
        self.wallSlide = False

        self.rect = self.image.get_rect()
        self.sweepRect = pygame.sprite.Sprite()
        self.sweepRect.rect = pygame.Rect(self.rect)

        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.prevPos = Vector2(self.rect.center)
        self.pos = Vector2(self.rect.center)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.lastCheckPoint = Vector2(0, 0)
        self.slidemod = 1.3
        self.isgrapple = 0


        self.grapple = Vector2(0, 0)
        self.grapplelen = 10
        self.grapplex = 0
        self.grappley = 0

        self.canWallJump = False
        self.canHook = False
        self.hookTimer = 0
        self.target = None
        self.hookRect = pygame.sprite.Sprite()
        self.hookRect.rect = pygame.Rect((0, 0, 1, 1))
        self.hookRect.rect.width = self.grapplelen * 16
        self.hookRect.rect.height = self.grapplelen * 32
        self.hookRect.center = self.rect.center

        self.invincibleTimer = 0
        self.hurtTimer = 0
        self.blinkTimer = 0
        self.health = PLAYER_MAX_HEALTH
        self.dead = False

    def move(self, direction):
        """Move the player when pressing a direction."""
        if self.hurtTimer:
            direction = 0

        if self.grounded:
            self.changeAnimation("walking")
            self.acc.x = 0
            self.vel.x = direction * PLAYER_MAX_VEL_X
            if direction < 0:
                self.flipped = True
            elif direction > 0:
                self.flipped = False
            else:
                self.vel.x *= PLAYER_FRICTION * self.game.deltaTime
                self.changeAnimation("idle")
        else:
            if abs(self.acc.x) >= PLAYER_MAX_ACC_X:
                self.acc.x = 0
            else:
                self.acc.x += direction * PLAYER_ACC * self.game.deltaTime

    def getHurt(self):
        if not self.invincibleTimer:
            if self.health:
                self.health -= 1
            if self.health <= 0:
                self.dead = True
            self.grounded = False
            self.wallSlide = False
            self.acc.y = 2000
            self.acc.x = 0
            self.vel.x = PLAYER_MAX_VEL_X if self.flipped else -PLAYER_MAX_VEL_X
            self.vel.y = PLAYER_JUMP_VEL
            self.hurtTimer = 1.0
            self.invincibleTimer = 2.5
            self.sfx.play("001_grunt_placeholder.wav")


    def setCheckPoint(self, pos):
        self.lastCheckPoint = Vector2(pos)

    def spawn(self):
        self.health = PLAYER_MAX_HEALTH
        self.grounded = False
        self.dead = False
        self.acc = Vector2(0, 0)
        self.vel = Vector2(0, 0)
        self.pos = Vector2(self.lastCheckPoint)
        self.rect.midbottom = self.pos

    def hookCheck(self):
        """Check if there is anything to grapple onto"""
        if self.hookTimer or not self.canHook:
            return

        if self.flipped:
            self.hookRect.rect.midright = self.rect.center
        else:
            self.hookRect.rect.midleft = self.rect.center


        hookCollision = pygame.sprite.spritecollide(self.hookRect, self.game.hookPoints, False)
        if hookCollision:
            self.sfx.play("005_throw.wav")
            self.hookTimer = 0.35
            self.grounded = False
            #for h in hookCollision:
            self.target = hookCollision[0]

            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery

            self.direction = 0.5 * math.pi + math.atan2(dy, dx)
            self.acc.x = 0
            self.acc.y = 0

            self.vel.x = math.sin(self.direction) * PLAYER_MAX_VEL_X
            self.vel.y = math.cos(self.direction) * PLAYER_JUMP_VEL


    def jump(self):
        """Apply jump when grounded"""
        if self.grounded or (self.wallSlide and self.canWallJump):
            self.changeAnimation("jumping")
            self.acc.y = 0
            self.vel.y = PLAYER_JUMP_VEL #if self.game.keys[pygame.K_SPACE] else PLAYER_JUMP_VEL * 0.2
            if not self.grounded:
                self.acc.x = -PLAYER_MAX_ACC_X if self.flipped else PLAYER_MAX_ACC_X
                self.vel.x = -PLAYER_MAX_VEL_X if self.flipped else PLAYER_MAX_VEL_X
                self.vel.y *= 0.75
            self.sfx.play("004_jump.wav")
            self.grounded = False
            self.wallSlide = False

    def slide(self):
        """Apply Slide when grounded"""
        if self.slide_timer <= 0:
            self.length_timer -= self.game.deltaTime
            self.image.fill((0, 0, 0))
            self.image.blit(self.player_image, (0, 0), self.animations["sliding"][0])
            hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
            if hits:
                self.vel.x = self.vel.x * self.slidemod
                self.sfx.play("008_slide.wav")
            if self.length_timer <= 0:
                self.slide_timer = 2
                self.length_timer = .3

    def grapple(self):
        if (self.isgrapple == 0):
            self.isgrapple = 1
        elif (self.isgrapple == 1):
            self.isgrapple = 0

        pos = pygame.mouse.get_pos()
        self.grapple = Vector2(pos)

    def processCollision(self):
        """Check for collisions vs the game objects"""
        movementCollisions = pygame.sprite.spritecollide(self.sweepRect, self.game.platforms, False)

        if movementCollisions:

            for h in movementCollisions:

                if "wall" in h.obtype.lower():
                    self.wallSlide = True

                if "boots" in h.obtype.lower() and not self.canWallJump:
                    self.canWallJump = True
                    self.setCheckPoint(h.rect.center)
                    print("BOOTS")

                if "rope" in h.obtype.lower() and not self.canHook:
                    self.canHook = True
                    self.setCheckPoint(h.rect.center)
                    print("ROPE")

                if "hurt" in h.obtype.lower() and not self.hurtTimer:
                    self.getHurt()

                elif "dead" in h.obtype.lower() or "death" in h.obtype.lower():
                    self.dead = True
                    self.getHurt()

                elif int(self.prevPosRect.bottom) <= h.rect.top and self.vel.y > 0 and \
                        "floor" in h.obtype.lower():
                    if self.prevPosRect.left < h.rect.left + 1 < self.prevPosRect.right or \
                            self.prevPosRect.left < h.rect.right < self.prevPosRect.right or \
                            h.rect.left < self.prevPosRect.centerx < h.rect.right:
                        self.acc.y = 0
                        self.vel.y = 0
                        self.pos.y = h.rect.top + 1
                        self.grounded = True
                        self.sfx.play("007_land.wav")

                elif int(self.prevPosRect.top) >= h.rect.bottom and self.vel.y < 0 and \
                        h.obtype.lower() in ["floor", "roof"]:

                    if self.prevPosRect.left < h.rect.left + 1 < self.prevPosRect.right or \
                            self.prevPosRect.left < h.rect.right < self.prevPosRect.right or \
                            h.rect.left < self.prevPosRect.centerx < h.rect.right:
                        self.acc.y = 0
                        self.vel.y = 0
                        self.pos.y = h.rect.bottom + self.rect.height

                elif int(self.rect.centerx) <= h.rect.left and self.vel.x > 0:
                    if abs(self.rect.bottom - h.rect.top) > 1 and \
                            h.obtype.lower() in ["floor", "roof", "wall"]:
                        self.acc.x = 0
                        self.vel.x = 0
                        self.pos.x = (h.rect.left + 1 - self.rect.width / 2)
                        if not self.grounded and "wall" in h.obtype.lower():
                            self.flipped = True

                elif int(self.rect.centerx) >= h.rect.right and self.vel.x < 0:
                    if abs(self.rect.bottom - h.rect.top) > 1 and \
                            h.obtype.lower() in ["floor", "roof", "wall"]:
                        self.acc.x = 0
                        self.vel.x = 0
                        self.pos.x = (h.rect.right + self.rect.width / 2)
                        if not self.grounded and "wall" in h.obtype.lower():
                            self.flipped = False


        else:
            self.wallSlide = False
            self.grounded = False
            self.changeAnimation("jumping")

    def update(self):
        """Update our player"""
        # TODO: Clean up draw calls. Should only need to blit one time.
        self.anime_timer += self.game.deltaTime
        self.stateTime += self.game.deltaTime

        if self.hookTimer > 0:
            self.hookTimer -= self.game.deltaTime
        else:
            self.hookTimer = 0
            self.target = None

        if self.invincibleTimer > 0:
            self.invincibleTimer -= self.game.deltaTime
            self.blinkTimer -= self.game.deltaTime
            if self.invincibleTimer <= 0:
                self.invincibleTimer = 0

            if self.blinkTimer <= 0:
                if self.image.get_alpha() >= 255:
                    self.image.set_alpha(64)
                else:
                    self.image.set_alpha(255)
                self.blinkTimer = 0.1
        else:
            self.blinkTimer = 0
            self.image.set_alpha(255)

        if self.slide_timer < 0:
            self.slide_timer = 0

        if self.hurtTimer:

            self.hurtTimer -= self.game.deltaTime
            if self.hurtTimer <= 0:
                self.hurtTimer = 0
                if self.dead:
                    self.spawn()

        if self.slide_timer:
            self.slide_timer -= self.game.deltaTime

        if self.rect.top >= self.game.cur_level.worldHeight:
            self.dead = True
            self.getHurt()

        if not self.grounded:
            self.acc.y += PLAYER_GRAV * self.game.deltaTime

        keys = self.game.keys
        events = self.game.events

        #TODO: Move input to an input method
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    self.jump()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.hookCheck()


        direction = int(keys[pygame.K_RIGHT] | keys[pygame.K_d]) - int(keys[pygame.K_LEFT] | keys[pygame.K_a])

        self.move(direction)

        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.slide()
            self.slidemod -= .015
            if self.slidemod < 0:
                self.slidemod = 0
        else:
            self.slidemod = 1.3

        self.prevPosRect = pygame.Rect(self.rect)

        #Movement
        self.vel += self.acc * self.game.deltaTime
        if abs(self.vel.x) > PLAYER_MAX_VEL_X:
            self.vel.x = PLAYER_MAX_VEL_X *(self.vel.x / abs(self.vel.x))

        self.pos += self.vel * self.game.deltaTime


        self.sweepRect.rect.left = min(self.prevPosRect.left, (self.pos.x - self.rect.width/2))
        self.sweepRect.rect.top = min(self.prevPosRect.top, (self.pos.y - self.rect.height))

        self.sweepRect.rect.width = self.rect.width + abs(self.prevPosRect.left - (self.pos.x - self.rect.width/2))
        self.sweepRect.rect.height = self.rect.height + abs((self.pos.y - self.rect.height) - self.prevPosRect.top)

        if "# Next Level" in self.game.cur_level.objects:
            if self.game.cur_level.objects["# Next Level"].rect.colliderect(self.rect):
                self.game.setGameMode("MainMenu")

        self.processCollision()
        self.rect.midbottom = self.pos

        #self.animateCharacter()
        self.playAudio()

    def changeAnimation(self, anim, frame = 0):
        self.stateTime = 0
        if self.current_anim != anim:
            self.current_frame = frame
            self.current_anim = anim

    def draw(self, screen, pos):
        """Update our self.image to the current sprite"""
        self.image.fill((0, 0, 0))

        if self.anime_timer >= 0.1:
            self.current_frame += 1
            self.anime_timer = 0
        if self.current_frame > len(self.animations[self.current_anim])-1 or self.current_frame < 0:
            self.current_frame = 0
        self.image.blit(self.player_image, (0, 0), self.animations[self.current_anim][self.current_frame])

        if self.flipped:
            self.image = pygame.transform.flip(self.image, self.flipped, False)

        screen.blit(self.image, pos)


        if self.hookTimer and self.target:
            lineStart = self.game.cur_level.worldToScreen(self.rect.center)
            lineEnd = self.game.cur_level.worldToScreen(self.target.rect.center)
            pygame.draw.line(screen, (128, 64, 32), lineStart, lineEnd, 5)


    def playAudio(self):
        if self.current_anim == "walking":
            if self.current_frame == 5:
                self.sfx.playIfNotBusy("003_movement_r.wav")
            elif self.current_frame == 1:
                self.sfx.playIfNotBusy("002_movement_l.wav")

        elif self.current_anim == "idle":
            self.idleTimer += self.game.deltaTime
            if self.idleTimer > self.health:
                self.sfx.playIfNotBusy(choice(self.idleSounds))
                self.idleTimer = 0


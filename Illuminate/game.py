
from map import *
from player import *
from levelobject import *
import settings
from audio_engine import *
from menu import *

#ToDo: Optimize Mask, currently very laggy.

initialize_audio_engine()
MusicPlaylist = ['Audio/Music/IlluminateSong1.ogg', 'Audio/Music/IlluminateSong2.ogg',
                 'Audio/Music/IlluminateSong3.ogg']
class Game:
    def __init__(self):
        """Set up our game app"""
        self.MusicPlayer = Music(MusicPlaylist)
        self.MusicPlayer.start_music()

        self.gameModes = ["MainMenu", "Start", "Play", "Exit"]
        self.pause = False
        self.mode = "MainMenu"

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.width = WIDTH
        self.height = HEIGHT
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.deltaTime = 0
        self.lightTimer = 0.05
        self.smolLightSize = randint(25, 30)
        self.bigLightSize = randint(100, 105)

        self.isRunning = False
        self.events = []
        self.keys = []
        self.player_image = pygame.image.load("image.png")
        self.cur_level = Map("./Level Directory/Level 00.txt", WIDTH, HEIGHT)

        pygame.font.init()
        self.debugFont = pygame.font.SysFont("Arial", 12)
        self.gameFontLarge = pygame.font.Font("./Assets/Fonts/Pixellari.ttf", 48)
        self.gameFontSmol = pygame.font.Font("./Assets/Fonts/Pixellari.ttf", 12)
        self.pauseText = self.gameFontLarge.render("PAUSE", True, (255, 255, 0))
        self.lifeText = self.gameFontSmol.render("LIFE:", True, (255, 255, 0))
        self.lifeTextSize = self.lifeText.get_rect()
        self.pausePos = (WIDTH/2 - self.pauseText.get_rect().width / 2,
                         HEIGHT/2 - self.pauseText.get_rect().height / 2)

        self.pauseScreen = pygame.Surface((WIDTH, HEIGHT))
        self.pauseScreen.fill((0, 0, 128))
        self.pauseScreen.set_alpha(128)


        self.mask = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()  # The mask surface works as the shadows, and the color key is the light.
        #self.mask.set_colorkey((255, 255, 255))
        self.mask.fill((0, 0, 0, 0))
        self.mosPos = pygame.mouse.get_pos()

        self.mainMenu = MainMenu(self.width, self.height)
        self.menuOption = ""


    def loadGameLevel(self, levelFile="./Level Directory/Level 00.txt"):
        """Reset or create new game"""
        self.allSprites = pygame.sprite.Group()

        self.platforms = pygame.sprite.Group()
        self.hookPoints = pygame.sprite.Group()

        self.cur_level.load(levelFile)
        self.player = Player(self)
        self.player.setCheckPoint(Vector2(self.cur_level.objects["# Spawn Point"].rect.midbottom))
        self.player.spawn()

        #self.player.pos = Vector2(self.cur_level.objects["# Spawn Point"].rect.midbottom)
        self.cur_level.setCameraPos(self.player.pos[0], self.player.pos[1])
        self.allSprites.add(self.player)

        for f in self.cur_level.objects.values():

            if "hook" in f.obtype.lower():
                self.hookPoints.add(f)
            else:
                self.platforms.add(f)

            self.allSprites.add(f)

        self.setGameMode("Play")

    def levelTransition(self):
        x = 255
        while x >= 0:
            self.screen.fill((0,0,0,x))

    def setGameMode(self, mode):
        """Set the mode of the game"""
        if mode in self.gameModes:
            self.mode = mode

    def startGame(self):
        """Start our game loop"""
        self.isRunning = True

    def run(self):
        """Run our game app"""
        while self.isRunning:
            self.deltaTime = self.clock.tick() / 1000
            self.input()
            self.update()
            self.draw()

    def input(self):
        """Process all our inputs"""
        self.events = pygame.event.get()
        self.keys = pygame.key.get_pressed()

        for event in self.events:
            if event.type == pygame.QUIT:
                self.isRunning = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause = not self.pause
                    self.mosPos = pygame.mouse.get_pos()
            if event.type == pygame.K_KP_ENTER:
                self.isRunning = True
            if event.type == pygame.MOUSEMOTION:
                self.mosPos = pygame.mouse.get_pos()
                if self.mode == "Play":
                    self.lightMaskUpdate(self.mosPos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    settings.DEBUG_MODE = not settings.DEBUG_MODE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.mode == "MainMenu":
                    self.setGameMode(self.mainMenu.click(self.mosPos[1]))

    def update(self):
        """Update everything in our game"""
        if self.mode == "MainMenu":
            self.mainMenu.update(self.mosPos[1])
        elif self.mode == "Start":
            self.loadGameLevel()
        elif self.mode == "Play" and not self.pause:
            self.lightTimer -= self.deltaTime
            self.allSprites.update()
            self.cur_level.setCameraPos(self.player.pos[0] - WIDTH * .5, self.player.pos[1] - HEIGHT * .5)
            self.lightMaskUpdate(self.mosPos)

        elif self.mode == "Exit":
            self.isRunning = False

    def lightMaskUpdate(self, pos):
        # creates a hole in the mask that follows the cursor
        if self.mode == "Play" and not self.pause:
            if self.lightTimer <= 0:
                self.lightTimer = 0.05
                self.smolLightSize = randint(35, 36)
                self.bigLightSize = randint(100, 105)
            self.mask.fill((0, 0, 0))
            playPos = self.cur_level.worldToScreen(self.player.rect.center)
            pygame.draw.circle(self.mask, (0, 0, 0, 128), (int(playPos[0]),int(playPos[1])), self.smolLightSize)

            pygame.draw.circle(self.mask, (255, 255, 255, 0), pos, self.bigLightSize)

            # draw.circle can be replaced by a group of squares drawing to make it more pixelated

    def drawPause(self):
        self.screen.blit(self.pauseScreen, (0, 0))
        self.screen.blit(self.pauseText, self.pausePos)

    def draw(self):
        """Draw the game"""
        self.screen.fill(BGCOLOR)

        if settings.DEBUG_MODE:
            self.screen.fill(DEBUG_BG_COLOR)

        if self.mode == "MainMenu":
            self.mainMenu.draw(self.screen)

        elif self.mode == "Play":
            # self.allSprites.draw(self.screen)
            playerDrawPos = self.cur_level.worldToScreen(self.player.pos)
            playerDrawPos[0] -= self.player.rect.width * 0.5
            playerDrawPos[1] -= self.player.rect.height
            self.cur_level.draw(self.screen)
            #self.screen.blit(self.player.image, playerDrawPos)

            self.player.draw(self.screen, playerDrawPos)

            for p in self.cur_level.objects.values():
                tempPos = self.cur_level.worldToScreen((p.rect.x, p.rect.y))
                if settings.DEBUG_MODE:
                    pygame.draw.rect(self.screen, PLATCOLOR, (tempPos[0], tempPos[1], p.rect.width, p.rect.height), 2)


            if not settings.DEBUG_MODE:
                self.screen.blit(self.mask, (0, 0))  # mask blits after canvas to be on top of it
            # blitting 'mask to screen' instead of 'mask to canvas to screen' makes it easier to remove the shadows
            # for debugging or a game mechanic, all you need to do is put 'screen.blit(mask, (0, 0))' in an if statement

            if self.player.health:
                self.screen.blit(self.lifeText, (5, 5))

                for x in range(self.player.health):
                    pygame.draw.rect(self.screen, (255,255,0), (self.lifeTextSize.right+10+x*11, 5, 10, self.lifeTextSize.height*0.75))

            if settings.DEBUG_MODE:
                playerSweepPos = self.cur_level.worldToScreen(self.player.sweepRect.rect.topleft)
                pygame.draw.rect(self.screen, (0, 255, 255), (playerSweepPos[0], playerSweepPos[1], self.player.sweepRect.rect.width, self.player.sweepRect.rect.height), 2)
                fpsCounter = self.debugFont.render("FPS: {:010.2f}".format(self.clock.get_fps()), True, (255, 255, 0))
                self.screen.blit(fpsCounter, (WIDTH - fpsCounter.get_rect().width - 1, 1))

            if self.pause:
                self.drawPause()


        pygame.display.update()


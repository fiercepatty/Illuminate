

import pygame
from settings import *

class LevelObject(pygame.sprite.Sprite):
    def __init__(self, id= None, obtype= "None", name= None, rect= pygame.Rect(0,0,1,1)):
        pygame.sprite.Sprite.__init__(self)
        self.ID = id
        self.obtype = obtype
        self.name = name
        self.rect = rect
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        pygame.draw.rect(self.image,PLATCOLOR, (0, 0, self.rect.width, self.rect.height), 2)



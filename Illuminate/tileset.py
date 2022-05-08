

import pygame


class TileSet(object):
    def __init__(self, *args):
        self.tileImageName = args[0]
        self.tileImage = pygame.image.load(args[0])
        self.tileImage.convert_alpha()
        self.tileImageWidth = int(args[1])
        self.tileImageHeight = int(args[2])
        self.tileSpacingX = int(args[3])
        self.tileSpacingY = int(args[4])
        self.tileImageNumRows = int(self.tileImage.get_height() / (self.tileImageHeight + self.tileSpacingY))
        self.tileImageNumCols = int(self.tileImage.get_width() / (self.tileImageWidth + self.tileSpacingX))
        self.tileImageNumTiles = self.tileImageNumCols * self.tileImageNumRows
        self.firstgid = 0

    def setBackgrounColor(self, color):
        self.tileImage = self.tileImage.convert()
        self.tileImage.set_colorkey(color)


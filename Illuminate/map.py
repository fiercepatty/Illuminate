

import pygame
from tileset import *
from levelobject import *
from pygame.math import Vector2

## Bits on the far end of the 32-bit global tile ID are used for tile flags
FLIPPED_HORIZONTALLY_FLAG = int('0x80000000', 16)
FLIPPED_VERTICALLY_FLAG   = int('0x40000000', 16)
FLIPPED_DIAGONALLY_FLAG   = int('0x20000000', 16)

class Map(object):
    """ A simple 2d map class. Loads from a "flare" txt file. """

    def __init__(self, fname, screenWidth, screenHeight):
        """Constructor for our map class"""
        self.mapWidth = 0                       #Width of the map in tiles
        self.mapHeight = 0                      #Height of the map in tiles
        self.tileWidth = 0                      #Width of each tile in pixels
        self.tileHeight = 0                     #Height of each tile in pixels
        self.worldWidth = 0
        self.worldHeight = 0
        self.orientation = None                 #Normally orthogonal
        self.tileImage = None               #Images that holds the tiles
        self.tileSets = []
        self.tileImageBackgroundColor = None    #The background color
        self.tileImageWidth = 0                 #Width of each tile on the tile sheet
        self.tileImageHeight = 0                #Height of each tile on the tile sheet
        self.tileSpacingX = 0                   #Horizontal Spacing
        self.tileSpacingY = 0                   #Vertical Spacing
        self.tileImageNumRows = 0
        self.tileImageNumCols = 0
        self.objects = {}
        self.tiles = []
        self.layers = []
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.cur_objid = ""

        #parse the data out
        self.load(fname)
        self.cameraPos = Vector2(0,0) #The World Space Position of the upper left of the camera.
        self.debug = False

    def load(self, fname):
        """Read our map file and collect the data"""
        self.tiles = []
        self.objects = {}
        self.layers = []
        self.tileSets = []
        mode = None

        fp = open(fname, "r")


        for line in fp:
            line = line.strip()
            if len(line) == 0:
                continue

            if line[0] == '[' and line[-1] == ']':
                mode = line[1:-1]
                continue

            if mode == "header":
                self.processHeaderLine(line)
            elif mode == "tilesets":
                self.processTilesetLine(line)
            elif mode == "layer":
                self.processLayerLine(line)
            elif mode.startswith("Collision"):
                self.processObjectLine(line)

        self.worldWidth = self.mapWidth * self.tileWidth
        self.worldHeight = self.mapHeight * self.tileHeight

        fp.close()

    def processHeaderLine(self, line):
        """Parse the header data"""
        elements = line.split('=')
        if len(elements) != 2:
            return
        key, value = elements

        if key == "width":
            self.mapWidth = int(value)
        elif key == "height":
            self.mapHeight = int(value)
        elif key == "tilewidth":
            self.tileWidth = int(value)
        elif key == "tileheight":
            self.tileHeight = int(value)
        elif key == "orientation":
            self.orientation = value
        elif key == "BackgroundColor":
            #BackgroundColor=66,107,107
            r, g, b = value.split(',')
            self.tileImageBackgroundColor = (int(r), int(g), int(b))


    def processTilesetLine(self, line):
        #tileset=nethack-3.4.3-32x32.png,32,32,0,0
        if len(line) >= 8 and line[0:8] == "tileset=" and\
            line.count(',') >= 4:
            elements = line[8:].split(',')


            tempTileSet = TileSet(*elements)
            self.tileImage = pygame.image.load(elements[0])

            """self.tileImageWidth = int(elements[1])
            self.tileImageHeight = int(elements[2])
            self.tileSpacingX = int(elements[3])
            self.tileSpacingY = int(elements[4])
            self.tileImageNumRows = int(self.tileImage.get_height() / (self.tileImageHeight + self.tileSpacingY))
            self.tileImageNumCols = int(self.tileImage.get_width() / (self.tileImageWidth + self.tileSpacingX))"""
            self.tileSets.append(tempTileSet)

            if len(self.tileSets) >= 2:
                self.tileSets[-1].firstgid = self.tileSets[-2].tileImageNumTiles + self.tileSets[-2].firstgid



    def processObjectLine(self, line):
        """Support Object Layers"""
        if line.startswith("#"):
            self.objects[line] = LevelObject()
            self.cur_objid = line

        elements = line.split('=')
        if len(elements) != 2:
            return
        key, value = elements

        t = ""
        r= []
        if key == "type":
           t = value.strip()
           self.objects[self.cur_objid].obtype = t

        elif key == "location":
            r = value.split(",")

            if len(r) != 4:
                return

            for i in range(len(r)):
                r[i] = int(r[i])

            r[0] = (r[0] - 0) * self.tileWidth
            r[1] = (r[1] - 0) *self.tileHeight

            r[2] = (r[2])*self.tileWidth

            r[3] = (r[3])*self.tileHeight


            self.objects[self.cur_objid].rect = pygame.Rect(r)

    def processLayerLine(self, line):
        #Todo: Support multiple layers.

        if line.count('='):
            if line.startswith("type"):
                pass
            if line.startswith("data"):
                self.layers.append([])
                #print(line, len(self.layers))
                return

        if line.count(',') >= self.mapWidth -1:
            elements = line.split(',')

            if elements[-1] == '':
                elements.remove(elements[-1])

            new_row = []

            for num in elements:
                new_row.append(int(num))
            #self.tiles.append(new_row)

            self.layers[len(self.layers) - 1].append(new_row)

    def draw(self, surf):
        """Draw our map to a surf"""



        for layer in self.layers:
            y = -(int(self.cameraPos[1]) % self.tileHeight)

            startRow = int(self.cameraPos[1]) // self.tileHeight
            numRows = int(self.screenHeight) // self.tileHeight + 1
            numCols = int(self.screenWidth) // self.tileWidth + 1

            for row in layer[startRow:startRow + numRows + 1]:
                x = -(int(self.cameraPos[0]) % self.tileWidth)
                startCol = int(self.cameraPos[0] // self.tileWidth)

                if row[startCol:startCol + numCols + 1].count(0) >= numCols+1:
                    #print(row[startCol:startCol + numCols + 1], row[startCol:startCol + numCols + 1].count(0), numCols)
                    y += self.tileHeight
                    continue

                for num in row[startCol:startCol + numCols + 1]:
                    if num == 0:
                        x += self.tileWidth
                        continue

                    num -= 1

                    #Checking bits to see if tile is flipped or rotated.
                    #http://doc.mapeditor.org/en/stable/reference/tmx-map-format/#tile-flipping

                    curTileSet = 0
                    flipped_horizontally = False
                    flipped_vertically = False
                    flipped_diagonally = False

                    if (num - self.tileSets[curTileSet].firstgid) < -1 or (num - self.tileSets[curTileSet].firstgid) > (self.tileSets[curTileSet].tileImageNumRows * self.tileSets[curTileSet].tileImageNumCols):

                        flipped_horizontally = bool(num & FLIPPED_HORIZONTALLY_FLAG)
                        flipped_vertically = bool(num & FLIPPED_VERTICALLY_FLAG)
                        flipped_diagonally = bool(num & FLIPPED_DIAGONALLY_FLAG)

                        num &= ~(FLIPPED_HORIZONTALLY_FLAG | FLIPPED_VERTICALLY_FLAG | FLIPPED_DIAGONALLY_FLAG)

                        num &= 0xFFFFFF

                    while num > (self.tileSets[curTileSet].firstgid + self.tileSets[curTileSet].tileImageNumTiles):
                        curTileSet += 1
                        if curTileSet > len(self.tileSets)-1:
                            curTileSet = 0
                            print(num, self.tileSets[curTileSet].firstgid)
                            break
                        else:
                            self.tileSets[curTileSet].firstgid

                    #print(num, tileOffset, curTileSet, self.tileSets[curTileSet].lastgid)
                    tile_row = (num - self.tileSets[curTileSet].firstgid) // self.tileSets[curTileSet].tileImageNumCols
                    tile_col = (num - self.tileSets[curTileSet].firstgid) % self.tileSets[curTileSet].tileImageNumCols
                    tile_x = tile_col * (self.tileWidth + self.tileSets[curTileSet].tileSpacingX)
                    tile_y = tile_row * (self.tileHeight + self.tileSets[curTileSet].tileSpacingY)

                    if flipped_diagonally or flipped_vertically or flipped_horizontally:
                        #blit that stuff
                        tempSurf = pygame.Surface((self.tileWidth, self.tileHeight))
                        tempSurf = tempSurf.convert()
                        tempSurf.set_colorkey((0, 0, 0))


                        tempSurf.blit(self.tileSets[curTileSet].tileImage, (0, 0), (tile_x, tile_y,
                                                                      self.tileWidth,
                                                                      self.tileHeight))

                        if flipped_diagonally:
                            tempSurf = pygame.transform.rotate(tempSurf, 90)

                        if flipped_horizontally or flipped_vertically:
                            tempSurf = pygame.transform.flip(tempSurf, flipped_horizontally, flipped_vertically)


                        surf.blit(tempSurf, (x, y))
                    else:
                        surf.blit(self.tileSets[curTileSet].tileImage, (x, y), (tile_x, tile_y,
                                                                      self.tileWidth,
                                                                      self.tileHeight))

                    x += self.tileWidth
                y += self.tileHeight

            if self.debug:
                for obj in self.objects:
                    sx, sy = self.worldToScreen((obj.rect[0], obj.rect[1]))

                    pygame.draw.rect(surf, pygame.Color("red"),
                                     (sx, sy, obj.rect[2], obj.rect[3]), 1)

    def setCameraPos(self, wx, wy):
        if wx < 0: wx = 0
        if wy < 0: wy = 0
        if wx > self.worldWidth - self.screenWidth:
            wx = self.worldWidth - self.screenWidth
        if wy > self.worldHeight - self.screenHeight:
            wy = self.worldHeight - self.screenHeight



        self.cameraPos[0] = wx
        self.cameraPos[1] = wy

    def worldToScreen(self, pos):
        return [pos[0] - self.cameraPos[0], pos[1] - self.cameraPos[1]]

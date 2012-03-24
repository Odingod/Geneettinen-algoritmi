# -*- coding: utf-8 -*-
import random
from creature import *#Creature, CreatureLabel, Generation
from food import Food, FoodLabel
import terrain
import io
from globals import *

class World(object):
    '''
    Object that contains all the creatures of the generation and food
    '''
    def __init__(self):
        # self.terrainGenerator = None
        self.terrain = []
        self.tiles = []
        self.creatures = {}
        self.foods = {}
        self.statistics = []
        self.maximum = 0
        self.total = 0
        self.average = 0.0

    def makeTerrain(self, terrainGenerator):
        """
        
        Arguments:
        - `width`:
        - `height`:
        - `drunkards`:
        """

        terrainGenerator.generate()
        self.terrain = terrainGenerator.terrain
        self.drawTerrain()

    def loadTerrain(self, filename):
        """
        
        Arguments:
        - `filename`: filename of terrain file
        """
        self.terrain = io.mapFileToArray(filename)
        self.drawTerrain()

    def drawTerrain(self):
        # loc = (20, 20)
        # key = getAssociatedKey(ID=self.getTerrainID(loc))
        # if not USE_GRAPHICS:
        #     self.addTile(Tile(key, loc))
        # else:
        #     self.addTile(TileLabel(key, loc, self))
        
        for x in xrange(len(self.terrain)):
            for y in xrange(len(self.terrain[0])):
                loc = (x, y)
                key = getAssociatedKey(ID=self.getTerrainID(loc))
                if not USE_GRAPHICS:
                    self.addTile(Tile(key, loc))
                else:
                    self.addTile(TileLabel(key, loc, self))


    def addTile(self, tile):
        self.tiles.append(tile)
        
    def addCreature(self, creature):
        '''
        Adds creature if there's no other creature at the same spot, else tries to put creature somewhere else
        '''
        # Minusta tämä pohjakoodi oli niin epäselvää, että minun oli pakko tehdä
        # oma versio... ottakaan  koodi pois kommenteista jos se toimi paremmin
        # tai oli mielestänne jotenkin selkeää
        
        # try:
        #     self.creatures[creature.loc]
        # except KeyError:
        #     self.creatures[creature.loc] = creature
        #     return
        # creature.loc = (randint(0, WIDTH), randint(0, HEIGHT))
        # self.addCreature(creature)
        inserted = False
        while not inserted:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            creature.loc = x, y
            terrainType = getAssociatedKey(ID=self.terrain[x][y])
            if creature.loc not in self.creatures and terrainType == 'grass':
                inserted = True
                self.creatures[creature.loc] = creature
        
    
    def addFood(self, food):
        '''
        Adds food if there's no other creature at the same spot, else tries to put food somewhere else
        '''

        # try:
        #     self.foods[food.loc]
        # except KeyError:
        #     self.foods[food.loc] = food
        #     return
        # food.loc = (randint(0, WIDTH), randint(0, HEIGHT))
        # self.addFood(food)

        inserted = False
        while not inserted:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            food.loc = x, y
            terrainType = getAssociatedKey(ID=self.terrain[x][y])
            if food.loc not in self.foods and terrainType != 'wall':
                inserted = True
                self.foods[food.loc] = food
    
    def removeFood(self, food):
        del self.foods[food.loc]
    
    def removeCreature(self, cre):
        del self.creatures[cre.loc]

    def updateLocation(self, creature, newloc):
        del self.creatures[creature.loc]
        self.creatures[newloc] = creature
        creature.loc = newloc

        if creature.isDead():
            creature.changePic()
        
    def getCreature(self,loc):
        try:
            return self.creatures[loc]
        except KeyError:
            return None
        
    def getFood(self,loc):
        try:
            return self.foods[loc]
        except KeyError:
            return None

    def getTerrainID(self, loc):
        try:
            return self.terrain[loc[0]][loc[1]]
        except KeyError:
            return None
        
    def removeEverything(self):
        for creature in self.creatures.values():
            self.removeCreature(creature)

        for food in self.foods.values():
            self.removeFood(food)
        
    def populate(self,generation=None, food_location='random'):
        if generation is not None:
            for cre in generation.creatures:
                self.addCreature(cre)

        else:
            for x in range(10):
                if not USE_GRAPHICS:
                    self.addCreature(Creature((randint(0, WIDTH), randint(0, HEIGHT)), NORTH))
                else:
                    self.addCreature(CreatureLabel(self, (randint(0, WIDTH), randint(0, HEIGHT))))
        
        if food_location == 'random':
            for x in range(200):
                if not USE_GRAPHICS:
                    self.addFood(Food((randint(0, WIDTH), randint(0, HEIGHT))))
                else:
                    self.addFood(FoodLabel(self, (randint(0, WIDTH), randint(0, HEIGHT))))

        elif food_location == 'middle':
            for i in range(15, 26):
                for j in range(15, 26):
                    self.addFood((Food(i, j) if not USE_GRAPHICS else FoodLabel(self, (i, j))))      

        elif food_location == 'corner':
            for i in range(WIDTH):
                for j in range(HEIGHT):
                    if (i < 5 or i > WIDTH - 6) and (j < 5 or j > HEIGHT - 6):
                        self.addFood((Food(i, j) if not USE_GRAPHICS else FoodLabel(self, (i, j))))  


class Statistics():
    def __init__(self, totaleaten, totalwalked):
        self.totaleaten = totaleaten
        self.totalwalked = totalwalked
    
class Tile(object):
    def __init__(self, key, loc):
        self.key = key
        self.loc = loc

class TileLabel(QLabel, Tile):
    def __init__(self, key, loc, parent):
        QLabel.__init__(self, parent)
        Tile.__init__(self, key, loc)
        self.resize(QSize(GRIDSIZE, GRIDSIZE))
        self.show()
        self.animationStep = 0
        self.originalPic = QPixmap.fromImage(TERRAINTYPEIMAGE[key])
        self.setPixmap(self.originalPic)
        self.setAttribute(Qt.WA_DeleteOnClose)

class WorldLabel(QWidget, World):
    def __init__(self, parent=None):        
        QWidget.__init__(self, parent)
        World.__init__(self)
        self.setLayout(None)
        self.resize(GRIDSIZE * WIDTH, GRIDSIZE * HEIGHT)
        self.bool = False
        
    # def drawBackground(self):
    #     """
    #     """
    #     for x in xrange(WIDTH):
    #         for y in xrange(HEIGHT):
    #             super(WorldLabel, self).

    
    def sizeHint(self, *args, **kwargs):
        return QSize(GRIDSIZE * (WIDTH + 1), GRIDSIZE * (HEIGHT + 1))
    
    def update(self):
        for tile in self.tiles:
            tile.move(tile.loc[0] * GRIDSIZE, tile.loc[1] * GRIDSIZE)
        for loc, cre in self.creatures.iteritems():
            cre.move(loc[0] * GRIDSIZE, loc[1] * GRIDSIZE)
    
    def updateFoods(self):
        for loc, food in self.foods.iteritems():
            food.move(loc[0] * GRIDSIZE, loc[1] * GRIDSIZE)

    
    def removeFood(self, food):
        food.setParent(None)
        super(WorldLabel, self).removeFood(food)
    
    def removeCreature(self, creature):
        creature.setParent(None)
        super(WorldLabel, self).removeCreature(creature)
    
    def populate(self,generation=None):
        super(WorldLabel, self).populate(generation)
        self.updateFoods()
        self.update()
        

# -*- coding: utf-8 -*-
import random
from creature import * #Creature, CreatureLabel, Generation
from food import Food, FoodLabel
import terrain
import io
from globals import *
import creature

class World(object):
    '''
    Object that contains all the creatures of the generation and food
    '''
    def __init__(self, wUSE_GRAPHICS=True, test=False):
        # self.terrainGenerator = None
        self.terrain = []
        self.tiles = []
        self.creatures = {}
        self.foods = {}
        self.USE_GRAPHICS = wUSE_GRAPHICS
        if test:
			global USE_GRAPHICS 
			USE_GRAPHICS = False

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
                if not self.USE_GRAPHICS:
                    self.addTile(Tile(key, loc))
                else:
                    self.addTile(TileLabel(key, loc, self))



    def addTile(self, tile):
        self.tiles.append(tile)
        
    def addCreature(self, creature, rando=True):
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
        tries = 0
        while not inserted and tries < 10:
            x = 0
            y = 0
            if rando:
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
            else:
                x = creature.loc[0]
                y = creature.loc[1]
            creature.loc = x, y
            # if not USE_GRAPHICS:
            #     print "x:", x, ", y:", y
            terrainType = getAssociatedKey(ID=self.terrain[x-1][y-1])
            #if creature.loc not in self.creatures and terrainType == 'grass':
            if creature.loc not in self.creatures and (terrainType != 'deep_water' and terrainType != 'mountain'):
                inserted = True
                self.creatures[creature.loc] = creature
                if self.USE_GRAPHICS:
                    creature.move(x * GRIDSIZE, y * GRIDSIZE)
            print terrainType, inserted
            tries += 1
            rando = True
    
    def addFood(self, food, rando=True):
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
        if not GAMEOFLIFE:
            inserted = False
            tries = 0
            while not inserted and tries < 10:
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                food.loc =x,y
                terrainType = getAssociatedKey(ID=self.terrain[x][y])
                if food.loc not in self.foods and (terrainType != 'mountain' and terrainType != 'deep_water'):
                    inserted = True
                    self.foods[food.loc] = food
                    if self.USE_GRAPHICS:
                        food.move(x * GRIDSIZE, y * GRIDSIZE)
                tries+=1
        
        
        else:
            x=food.loc[0]
            y=food.loc[1]
            terrainType = getAssociatedKey(ID=self.terrain[x][y])
            if food.loc not in self.foods and (terrainType != 'mountain' and terrainType != 'deep_water'):
                inserted = True
                self.foods[food.loc] = food
                if self.USE_GRAPHICS:
                    food.move(x * GRIDSIZE, y * GRIDSIZE)


        
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

    def removeCreatures(self):
        for creature in self.creatures.values():
            self.removeCreature(creature)

    def removeFoods(self):
        for food in self.foods.values():
            self.removeFood(food)
       
    def removeEverything(self):
        self.removeCreatures()
        self.removeFoods()
         
    def populate(self,generation=None, foodgeneration=None):

        if generation is not None:
            for cre in generation.creatures:
                self.addCreature(cre)

        else:
            for x in range((WIDTH * HEIGHT) / 160):
                if not self.USE_GRAPHICS:
                    self.addCreature(creature.Creature((randint(0, WIDTH), randint(0, HEIGHT)), NORTH, self, None, True))
                else:
                    self.addCreature(CreatureLabel(self, (randint(0, WIDTH), randint(0, HEIGHT))))
        

        if not GAMEOFLIFE or foodgeneration==None:
            for x in range(SCALEDFOOD):
                if not USE_GRAPHICS:
                    self.addFood(Food((randint(0, WIDTH), randint(0, HEIGHT))))
                else:
                    self.addFood(FoodLabel(self, (randint(0, WIDTH), randint(0, HEIGHT))))
                    
        else:
            for food in foodgeneration.foods.values():
                self.addFood(food)
                


    
                     
    def changeToWorldLabel(self,parent):
        world = WorldLabel(parent)
        parent.setCentralWidget(world)
        world.terrain = self.terrain
        world.tiles = self.tiles
        world.drawTerrain()
        for food in self.foods:
            world.addFood(FoodLabel(world, self.foods[food].loc))
        world.updateFoods()
        for cre in self.creatures:
            creature=CreatureLabel(world, self.creatures[cre].loc, self.creatures[cre].genome)
            creature.eaten = self.creatures[cre].eaten
            creature.calories = self.creatures[cre].calories
            creature.dead = self.creatures[cre].dead
            creature.miles= self.creatures[cre].miles
            world.addCreature(creature) 
        return world
            
            
class Statistics():
    def __init__(self, totaleaten, totalwalked, totalalive=None):
        self.totaleaten = totaleaten
        self.totalwalked = totalwalked
        self.totalalive=totalalive
        
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
        self.move(loc[0] * GRIDSIZE, loc[1] * GRIDSIZE)

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
        # for tile in self.tiles:
        #     tile.move(tile.loc[0] * GRIDSIZE, tile.loc[1] * GRIDSIZE)
        for loc, cre in self.creatures.iteritems():
            cre.move(loc[0] * GRIDSIZE, loc[1] * GRIDSIZE)
    
    def updateFoods(self):
        if GAMEOFLIFE:
            for loc, food in self.foods.iteritems():
                if food.isAlive():
                    food.move(loc[0] * GRIDSIZE, loc[1] * GRIDSIZE)
        else:
            for loc, food in self.foods.iteritems():
                food.move(loc[0] * GRIDSIZE, loc[1] * GRIDSIZE)
    
    def removeFood(self, food):
        food.setParent(None)
        super(WorldLabel, self).removeFood(food)
    
    def removeCreature(self, creature):
        creature.setParent(None)
        super(WorldLabel, self).removeCreature(creature)
    
    def populate(self,generation=None, foodgeneration=None):
        super(WorldLabel, self).populate(generation, foodgeneration)
        self.updateFoods()
        self.update()
        
    def changeToWorld(self):
        world = World(wUSE_GRAPHICS=False)
        world.terrain = self.terrain
        world.tiles = self.tiles
        for cre in self.creatures:
            creature=Creature(self.creatures[cre].loc, self.creatures[cre].heading, world, self.creatures[cre].genome)
            creature.eaten = self.creatures[cre].eaten
            creature.calories = self.creatures[cre].calories
            creature.dead = self.creatures[cre].dead
            creature.miles= self.creatures[cre].miles
            world.addCreature(creature)
        for food in self.foods:
            world.addFood(Food(self.foods[food].loc))
        return world
        

import random
from globals import *

X = 0
Y = 1

class Drunkard(object):
    
    def __init__(self, terrain, steps=45, terrainType=1):

        self.choices = {
            'Up': 0,
            'Left': 1,
            'Right': 2,
            'Down': 3
            }
        
        self.terrain = terrain
        self.isDead = False
        self.terrainHeight = len(self.terrain)
        self.terrainWidth = len(self.terrain[0])
        self.location = (random.randint(0, self.terrainWidth - 1), random.randint(0, self.terrainHeight - 1))
        self.stepCount = 0
        self.maxSteps = steps
        self.forbiddenTypes = [2]
        self.terrainType = terrainType
        
    def move(self):
        choice = random.choice(self.choices.values())
        location = self.location
        if choice == 0:
            if self.canMoveTo((location[X], location[Y] + 1)):
                self.location = (location[X], location[Y] + 1)

        elif choice == 1:
            if self.canMoveTo((location[X] - 1, location[Y])):
                self.location = (location[X] - 1, location[Y])

        elif choice == 2:
            if self.canMoveTo((location[X] + 1, location[Y])):
                self.location = (location[X] + 1, location[Y])
            
        elif choice == 3:
            if self.canMoveTo((location[X], location[Y] - 1)):
                self.location = (location[X], location[Y] - 1)
        
        if self.stepCount < self.maxSteps:
            self.stepCount += 1
            self.modifyTerrain(location)
        else:
            self.die()

    def die(self):
        self.isDead = True

    def modifyTerrain(self, location):
        #print location
        #print "Alkuperainen:", self.terrain[location[X]][location[Y]]
        self.terrain[location[X]][location[Y]] = self.terrainType
        #print "Muokattu:", self.terrain[location[X]][location[Y]]

    def canMoveTo(self, to):
        if 0 < to[X] < self.terrainWidth and 0 < to[Y] < self.terrainHeight:
            if self.terrain[self.location[X]][self.location[Y]] not in self.forbiddenTypes:
                return True
        return False

#class WaterDrunkard(Drunkard):
    """
    """
#    def __init__(self, terrain, steps=45):
#        Drunkard.__init__(self, terrain, steps, 2)
#        self.forbiddenTypes = []


class DrunkardTerrainGenerator(object):
    """
    """
    def __init__(self, width, height, amountOfDrunkards=40):
        """
        """
        self.drunkards = []
        self.terr = [None] * width

        self.terrainWidth = width
        self.terrainHeight = height
        self.amountOfDrunkards = amountOfDrunkards
        
        for x in xrange(self.terrainWidth):
            self.terr[x] = [0] * self.terrainHeight

        for x in xrange(amountOfDrunkards):
            self.drunkards.append(Drunkard(self.terr))
        
    def generate(self):
        for drunkard in self.drunkards:
            while not drunkard.isDead:
                drunkard.move()
    
    def printTerrain(self):
        row = ""
        for x in range(len(self.terr)):
            for y in range(len(self.terr[0])):
                row  += "[" + str(self.terr[x][y]) + "]"
            print row
            row = ""

#if __name__ == '__main__':
    #terrain = DrunkardTerrainGenerator(20, 20, 25)
    #print terrain.drunkens
    #terrain.generate()
    #terrain.printTerrain()

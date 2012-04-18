import random
import globals
import io
import math


X = 0
Y = 1

def printTerrain(terr):
    row = ""
    for x in range(len(terr)):
        for y in range(len(terr[0])):
            row  += "[" + str(terr[x][y]) + "]"
        print row
        row = ""

class NoiseMapGenerator:
    
    def __init__(self, octaves=3, width=globals.WIDTH, height=globals.HEIGHT, roughness=6.0, seeded=globals.SEED):
        self.octaves = octaves
        self.width = width
        self.height = height
        self.zoom = 20.0
        self.roughness = float(roughness)
        self.offsetx = 0
        self.offsety = 0
        self.terrain = [[None for y in xrange(self.height)] for x in xrange(self.width)]
        #primes = self.prime(100000)
        random.seed(seeded)
        self.primel = [random.choice([7, 11, 13, 17, 19, 23, 29]), 
                  random.choice([31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79]),
                  random.choice([60413, 60427, 60443, 60449, 60457, 60493, 60497, 60509, 60521, 
                                 60527, 60539, 60589, 60601, 60607, 60611, 60617, 60623, 60631, 
                                 60637, 60647, 60649, 60659, 60661, 60679, 60689, 60703, 60719, 
                                 60727, 60733, 60737, 60757, 60761, 60763, 60773, 60779, 60793, 
                                 60811, 60821, 60859, 60869, 60887, 60889, 60899, 60901, 60913, 
                                 60917, 60919, 60923, 60937, 60943, 60953, 60961])]
        #print [p for p in primes if 60400 < p < 61000]
        
        
    '''
    def prime(self, n):
            """
            Generate list of primes.
            """
            primes = [2]
            for m in range(3,n,2):
                if all(m%p for p in primes):
                    primes.append(m)
            return primes
    '''
    
    def generate(self):
        for x in xrange(self.width):
            for y in xrange(self.height):
                noiseval = 0
                for a in xrange(self.octaves-1):
                    freq = float(2.0 ** a)
                    ampl = float(self.roughness ** a)                
                    noiseval += self.perlin_noise((y + self.offsety) * (freq / self.zoom), ((x + self.offsetx)/ (freq * self.zoom)) * ampl)
                i = int(noiseval * 128 + 128)
                if i < 20:
                    #Deep Water
                    self.terrain[x][y] = 1
                elif i < 71:
                    #Water
                    self.terrain[x][y] = 2
                elif i < 106:
                    #Coast
                    self.terrain[x][y] = 3
                elif i < 156:
                    #Grass
                    self.terrain[x][y] = 4
                elif i < 237:
                    #Forest
                    self.terrain[x][y] = 5
                elif i < 288:
                    #Hill
                    self.terrain[x][y] = 6
                else:
                    #Mountain
                    self.terrain[x][y] = 7
    
    def makenoise(self, x, y):
        '''
        A pseudo-random number generator
        '''
        n = int(x) + int(y) * self.primel[1]
        n=(n << self.primel[0]) ^ n
        nn=int((n * (n * n * self.primel[2] + 19990303) + 1376312589) & 0x7fffffff)
        return 1.0 - (nn / 1073741824.0)
    
    def interpolate(self, a, b ,x):
        ft = x * math.pi
        f = (1 - math.cos(ft)) * 0.5
        return a * (1 - f) + b * f
    
    def perlin_noise(self, x, y):
        '''
        Generates noise based on the position
        '''
        flrx = math.floor(x)
        flry = math.floor(y)
        s = self.makenoise(flrx, flry)
        t = self.makenoise(flrx+1, flry)
        u = self.makenoise(flrx, flry+1)
        v = self.makenoise(flrx+1, flry+1)
        
        i1 = self.interpolate(s, t, x - flrx)
        i2 = self.interpolate(u, v, x - flrx)
        return self.interpolate(i1, i2, y - flry)
    
    def getTerrainData(self):
        return self.terrain

    def saveMap(self, filename=""):
        io.arrayToFile(self.terrain, filename)

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
        self.terrain[location[X]][location[Y]] = self.terrainType
        
    def canMoveTo(self, to):
        if 0 < to[X] < self.terrainWidth and 0 < to[Y] < self.terrainHeight:
            if self.terrain[self.location[X]][self.location[Y]] not in self.forbiddenTypes:
                return True
        return False

class WaterDrunkard(Drunkard):
    def __init__(self, terrain, steps=40):
        Drunkard.__init__(self, terrain, steps, 2)
        self.forbiddenTypes = []

    def move(self):
        choice = random.choice(self.choices.values())
        location = self.location
        if choice == 0 or choice == 2:
            if self.canMoveTo((location[X], location[Y] + 1)):
                self.location = (location[X], location[Y] + 1)
                
        elif choice == 1 or choice == 3:
            if self.canMoveTo((location[X] - 1, location[Y])):
                self.location = (location[X] - 1, location[Y])

        if self.stepCount < self.maxSteps:
            self.stepCount += 1
            self.modifyTerrain(location)
        else:
            self.die()   
        
class DrunkardTerrainGenerator(object):
    def __init__(self, width=globals.WIDTH + 1, height=globals.HEIGHT + 1, amountOfDrunkards=-1, generateWater=False):
        self.terrain = [None] * width
        if amountOfDrunkards == -1:
            self.amountOfDrunkards = (globals.WIDTH+globals.HEIGHT + random.randint(0, 25))

        else:
            self.amountOfDrunkards = amountOfDrunkards
        self.generateWater = generateWater

        for x in xrange(width):
            self.terrain[x] = [0] * height
            
        self.drunkards = []
        for x in xrange(self.amountOfDrunkards):
            self.drunkards.append(Drunkard(self.terrain))
    
        if generateWater:
            self.waterDrunkards = []
        
            for x in xrange(self.amountOfDrunkards):
                self.waterDrunkards.append(WaterDrunkard(self.terrain))

    def generate(self):
        if self.generateWater:
            for waterDrunkard in self.waterDrunkards:
                while not waterDrunkard.isDead:
                    waterDrunkard.move()

        for drunkard in self.drunkards:
            while not drunkard.isDead:
                drunkard.move()

    def getTerrainData(self):
        return self.terrain

    def saveMap(self, filename=""):
        io.arrayToFile(self.terrain, filename)

if __name__ == '__main__':
    #terrainGenerator = DrunkardTerrainGenerator()
    #terrainGenerator.generate()
    #printTerrain(terrainGenerator.terrain)
    #terrainGenerator.saveMap()
    
    #print '\n'
    irr = 0
    while irr < 10: 
        terrainGenerator = NoiseMapGenerator(seeded=random.random())
        terrainGenerator.generate()
        terrainGenerator.saveMap()
        irr+=1
    #printTerrain(terrainGenerator.terrain)
    terrainGenerator.saveMap()

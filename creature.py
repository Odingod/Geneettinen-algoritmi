# -*- coding: utf-8 -*-

from PySide.QtCore import *
from PySide.QtGui import *
from random import randint
from random import choice


#from world import *
#from gen import *
#from world import *
from globals import *
import gen

# NORTH=(0,-1)
# EAST=(1,0)
# SOUTH=(0,1)
# WEST=(-1,0)
# CREATURE_PIC=[QImage('jpac.png').transformed(QTransform().rotate(a)) for a in xrange(0,360,90)]
# CORPSE_PIC=QImage('pacdead.png')
# WIDTH=40
# HEIGHT=40
# GRIDSIZE=16
# USE_GRAPHICS = True
# MUTATE=10 #chance of mutation in ‰


class WorldRetriever(object):
    def __init__(self, w):
        self.world = w
        global world
        world = self.world

class Creature(object):
    '''
    Basic creature
    
    Contains all the necessary data to simulate the creature. 
    genome contains creature's genome, memory it's current state and loc it's location.
    Genome is a 16*4 array of tuples. Creature's next action and state is decided by the genome.
    It takes the tuple from genome[memory][sight] where sight is based on what's infront of the creature.
    Then it does the action based on the tuples first member and sets it's own memory to the second member.
    
    '''
    def __init__(self,loc,heading,genome=None):
        self.loc=loc
        self.heading=heading
        self.sight=0
        self.memory=0
        self.walked = 0
        if genome == None:
            self.genome=[[(randint(0,2),randint(0,15)) for y in xrange(4)] for x in xrange(16)]
        else:self.genome=genome
            
        self.eaten=1
        self.calories = 500
        self.dead = False


    def isDead(self):
        return self.dead
    
    def changePic(self):
        return
    
    def moveSelf(self):
        '''
        Moves self to the next location if it doesn't already contain a creature
        
        Also eats food  if there is some on the new square
        '''
        if self.loc != self.nextLoc():
            self.walked+=1
            
        newloc=self.nextLoc()
        if world.getCreature(newloc)==None:
            self.calories -= 10
            if self.calories < 0:
                self.dead = True
            world.updateLocation(self, newloc)
        if world.getFood(newloc)!=None:
            world.removeFood(world.getFood(newloc))
            self.eaten += 1
            self.calories += 50
            
    def nextLoc(self):
        '''
        Tells the creature's next possible location
        '''
        newloc=(self.loc[0]+self.heading[0],self.loc[1]+self.heading[1])
        if newloc[0]<0:newloc=(0,newloc[1])
        elif newloc[0]> WIDTH:newloc=(WIDTH,newloc[1])
        if newloc[1]<0:newloc=(newloc[0],0)
        elif newloc[1]> HEIGHT:newloc=(newloc[0],HEIGHT)
        return newloc
    
    def turnSelf(self,heading):
        self.heading=heading
        
    def doTurn(self):
        '''
        Executes the turn
        
        First updates the sight and then does the action defined by the genome
        '''
        if not self.isDead():
            self.updateSelf()
            self.doAction()
    
    def updateSelf(self):
        '''
        Updates sight based on what is infront of the creature
        '''
        if world.getCreature(self.nextLoc())!=None and world.getCreature(self.nextLoc())!=self:
            #saw someone else
            self.sight=1
        elif world.getFood(self.nextLoc())!=None:
            #saw food
            self.sight=2
        elif self.nextLoc()==self.loc :
            #saw wall
            self.sight=3
        else: self.sight=0 #saw nothing
    
    def turnLeft(self):
        if self.heading == NORTH:self.turnSelf(WEST)
        elif self.heading == WEST:self.turnSelf(SOUTH)
        elif self.heading == SOUTH:self.turnSelf(EAST)
        elif self.heading == EAST:self.turnSelf(NORTH)
    
    def turnRight(self):
        if self.heading == NORTH:self.turnSelf(EAST)
        elif self.heading == WEST:self.turnSelf(NORTH)
        elif self.heading == SOUTH:self.turnSelf(WEST)
        elif self.heading == EAST:self.turnSelf(SOUTH)
        
    def doAction(self):
        '''
        Does the action defined by the genome
        '''
        #if self.sight!=0:  print self.memory,self.sight
        a,b=self.genome[self.memory][self.sight]
        if a == 0:self.turnLeft()
        elif a == 1:self.turnRight()
        elif a == 2:self.moveSelf()
        self.memory=b
        
    def combine(self,other):
        '''
        Mates self and other and produces another creature and returns it.
        
        New creature's genome's first half comes from self and the second part from the other.
        The splitting point point is chosen by random.
        This could be a bit more elaborate.
        http://en.wikipedia.org/wiki/Crossover_%28genetic_algorithm%29
        ''' 
        newGenome=[[None]*4 for x in xrange(16)]
        a,b=randint(0,3),randint(0,15)
        for x in xrange(16):
            for y in xrange(4):
                if randint(0,1000)<MUTATE:
                    newGenome[x][y]=(randint(0,2),randint(0,15))
                elif x==b and y>a:
                    newGenome[x][y]=other.genome[x][y]
                elif x>b:
                    newGenome[x][y]=other.genome[x][y]
                else:
                    newGenome[x][y]=self.genome[x][y]
        return CreatureLabel(world,(randint(0,WIDTH),randint(0,HEIGHT)),newGenome) if USE_GRAPHICS else Creature((randint(0,WIDTH),randint(0,HEIGHT)),NORTH,newGenome)
        
        

class CreatureLabel(QLabel,Creature):
    '''
    Class that inherits from Creature and QLabel and that can be added to the WorldLabel
    '''
    def __init__(self,parent,loc,genome=None):
 
        QLabel.__init__(self,parent)
        Creature.__init__(self, loc,NORTH,genome)
        self.resize(GRIDSIZE,GRIDSIZE)
        self.show()
        self.setPixmap(QPixmap.fromImage(CREATURE_PIC[3]))


    def turnSelf(self,heading):
        '''
        Turns the picture
        '''
        super(CreatureLabel,self).turnSelf(heading)
        a=0
        if heading == NORTH: a=3
        elif heading == EAST: a=0
        elif heading == SOUTH: a=1
        elif heading== WEST: a=2
        self.setPixmap(QPixmap.fromImage(CREATURE_PIC[a]))

    def changePic(self):
        '''
        pic changes to corpse if creature dies
        '''
        super(CreatureLabel,self).changePic()
        self.setPixmap(QPixmap.fromImage(CORPSE_PIC))

class Generation(object):
    '''
    Contains all the creatures of one generation
    
    Has function to produce new generation based on the current one
    '''
    def __init__(self,size,creatures=None):
        self.size=size
        if creatures== None:
            self.creatures=[]
            for x in xrange(self.size):
                self.creatures.append(CreatureLabel(world,(randint(0,WIDTH),randint(0,HEIGHT))) if USE_GRAPHICS else Creature((randint(0,WIDTH),randint(0,HEIGHT)),NORTH))
        else:self.creatures=creatures



    def nextGeneration(self):
        '''
        Generates new generation and returns it.
        
        First it creates a list candidates which contains list indices of creatures.
        The more the creature has eaten the more places it gets on the candidate list.
        Then new creatures are created by randomly choosing the creatures to combine.         
        '''
        candidates=sum([[i]*self.creatures[i].eaten for i in xrange(len(self.creatures))],[]) #sum is used to flatten the list of lists
        creatures=[]
        for x in xrange(self.size):
            creatures.append(self.creatures[choice(candidates)].combine(self.creatures[choice(candidates)]))
        return Generation(self.size,creatures)
    
    def totalEaten(self):
        '''
        Returns how much the entire genearation has eaten
        '''
        i=0
        for cre in self.creatures:
            i+=cre.eaten-1
        return i
    
    def totalWalked(self):
        '''
        Return how much the entire generation has walked
        '''
    
        i = 0
        for cre in self.creatures:
            i+=cre.walked
        return i    

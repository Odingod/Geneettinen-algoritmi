# -*- coding: utf-8 -*-
'''
Pohjakoodia geneettisen algoritmin projektiin


Kehitysideoita:
pienempiä:
-tallennus/lataus (yksittäisen otuksen tai koko sukupolven)
-gui-härpäkkeitä (asetuksia, tilastoja ym.)
-asetuksia
    -otusten määrä ja tyyppi
    -ruoan määrä
    -kartan koko
    -vuoden pituus
    -genomin koko
    -algoritmi
-haju (otus 'haistaa' onko lähellä ruokaa)
-erilaisia ruoan asetteluita ja asetuksia 
    -määrä
    -onko ruoan määrä aina sama (eli ilmestyykö uutta kun vanhaa syödään)
    -ruokaa vain tietyillä alueilla
    -ruoka on ryppäissä
-vesi,seinät,
-kartan generointia, karttaeditori tai kartan tuonti kuvasta 
-kartassa useampia tasoja
-lentävät otukset
-uivat otukset(joita rannoilla kävelevät syövät)
-vesi(erikseen uinti ja kävely eteenpäin)
-erilaiset ruoat(hidastaa, pysäyttää, sekoittaa, ym.)
-toisia otuksia syövät otukset (oma Generation)
-samassa maailmassa kaksi eri sukupolvea jotka kehittyvät eri algoritmeilla
-eri algoritmeja

isompia:
-parempi algoritmi
-pieni skriptikieli jolla voisi kirjoitella omia otuksia
-sen sijaan että optimoitaisiin yksittäisen otuksen fitnessiä, vertailtaisiin sukupolvia ja valittaisiin jatkoon se joka söi yhteensä eniten
-voisi yrittää saada olioita tekemään jotain yksinkertaisia tehtäviä esim. kuljeta esineitä 'pesään', ole tietyllä alueella. Näissä pitäisi keksiä miten oliot pisteytetään.
-otusten välinen kommunikointi(lähetä oma tila)
-hiiriohjaus
    -ruokaa tähän 
    -näytä olion tiedot
    -siirrä oliota
    -zoomaus
    -ym.


    

'''
'''
Created on Jun 16, 2011

@author: anttir
'''

from PySide.QtCore import *
from PySide.QtGui import *
from random import randint
from random import choice
import sys,time
NORTH=(0,-1)
EAST=(1,0)
SOUTH=(0,1)
WEST=(-1,0)
WIDTH=40
HEIGHT=40
GRIDSIZE=16
global USE_GRAPHICS
USE_GRAPHICS=True
CREATURE_PIC=[QImage('jpac.png').transformed(QTransform().rotate(a)) for a in xrange(0,360,90)]
FOOD_PIC=QImage('food16.png')
MUTATE=10 #chance of mutation in ‰

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
        if genome == None:
            self.genome=[[(randint(0,2),randint(0,15)) for y in xrange(4)] for x in xrange(16)]
        else:self.genome=genome
            
        self.eaten=1
    
    def moveSelf(self):
        '''
        Moves self to the next location if it doesn't already contain a creature
        
        Also eats food  if there is some on the new square
        '''
        newloc=self.nextLoc()
        if world.getCreature(newloc)==None:
            world.updateLocation(self, newloc)
        if world.getFood(newloc)!=None:
            world.removeFood(world.getFood(newloc))
            self.eaten += 1
            
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
    

        
        
    
class Food(object):
    '''
    Very basic food object
    '''
    def __init__(self,loc):
        self.loc=loc
        
        
class FoodLabel(QLabel,Food):
    '''
    Object that can be added to WorldLabel
    '''
    def __init__(self,parent,loc):
        QLabel.__init__(self,parent)
        Food.__init__(self, loc)
        self.resize(QSize(GRIDSIZE,GRIDSIZE))
        self.show()
        self.animationStep=0
        self.originalPic=QPixmap.fromImage(FOOD_PIC)
        self.setPixmap(self.originalPic)
        self.setAttribute(Qt.WA_DeleteOnClose)
    
    def animate(self):
        self.setPixmap(self.originalPic.transformed(QTransform().rotate([-45,0,45,0][self.animationStep])))
        self.animationStep=(self.animationStep+1)%4  
        
        
class World(object):
    '''
    Object that contains all the creatures of the generation and food
    '''
    def __init__(self):
        self.creatures={}
        self.foods={}
        
    def addCreature(self,creature):
        '''
        Adds creature if there's no other creature at the same spot, else tries to put creature somewhere else
        '''
        try:
            self.creatures[creature.loc]
        except KeyError:
            self.creatures[creature.loc]=creature
            return
        creature.loc=(randint(0,WIDTH),randint(0,HEIGHT))
        self.addCreature(creature)
        
    
    def addFood(self, food):
        '''
        Adds food if there's no other creature at the same spot, else tries to put food somewhere else
        '''
        try:
            self.foods[food.loc]
        except KeyError:
            self.foods[food.loc]=food
            return
        food.loc=(randint(0,WIDTH),randint(0,HEIGHT))
        self.addFood(food)
    
    def removeFood(self,food):
        del self.foods[food.loc]
    
    def removeCreature(self,cre):
        del self.creatures[cre.loc]

    def updateLocation(self,creature,newloc):
        del self.creatures[creature.loc]
        self.creatures[newloc]=creature
        creature.loc=newloc
        
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
        
    def removeEverything(self):
        for creature in self.creatures.values():
            self.removeCreature(creature)
        for food in self.foods.values():
            self.removeFood(food)
        
    def populate(self,generation=None, food_location='random'):
        if generation!= None:
            for cre in generation.creatures:
                self.addCreature(cre)
        else:
            for x in range(10):
                self.addCreature(Creature((randint(0,WIDTH),randint(0,HEIGHT)),NORTH) if not USE_GRAPHICS else CreatureLabel(self,(randint(0,WIDTH),randint(0,HEIGHT))))
        
        if food_location=='random':
            for x in range(200):
                self.addFood(Food((randint(0,WIDTH),randint(0,HEIGHT))) if not USE_GRAPHICS else FoodLabel(self,(randint(0,WIDTH),randint(0,HEIGHT))))
        elif food_location=='middle':
            for i in range(15, 26):
                for j in range(15, 26):
                    self.addFood((Food(i, j) if not USE_GRAPHICS else FoodLabel(self, (i,j))))      
        elif food_location=='corner':
            for i in range(WIDTH):
                for j in range(HEIGHT):
                    if (i<5 or i>WIDTH-6) and (j<5 or j>HEIGHT-6):
                        self.addFood((Food(i, j) if not USE_GRAPHICS else FoodLabel(self, (i,j))))  

    

                
class WorldLabel(QWidget,World):
    def __init__(self,parent=None):        
        QWidget.__init__(self,parent)
        World.__init__(self)
        self.setLayout(None)
        self.resize(GRIDSIZE*WIDTH,GRIDSIZE*HEIGHT)
        self.bool=False
    
    def sizeHint(self, *args, **kwargs):
        return QSize(GRIDSIZE*(WIDTH+1),GRIDSIZE*(HEIGHT+1))
    
    def update(self):
        for loc,cre in self.creatures.iteritems():
            cre.move(loc[0]*GRIDSIZE,loc[1]*GRIDSIZE)
    
    def updateFoods(self):
        for loc,food in self.foods.iteritems():
            food.move(loc[0]*GRIDSIZE,loc[1]*GRIDSIZE)
    
    def removeFood(self,food):
        food.setParent(None)
        super(WorldLabel,self).removeFood(food)
    
    def removeCreature(self,creature):
        creature.setParent(None)
        super(WorldLabel,self).removeCreature(creature)
    
    def populate(self,generation=None):
        super(WorldLabel,self).populate(generation)
        self.updateFoods()
        self.update()
        
        
class MainWindow(QMainWindow):   
    def __init__(self):
        self.running=True
        self.highscore=0
        QMainWindow.__init__(self)     
        
        self.menubar=QMenuBar(self)
        self.setMenuBar(self.menubar)
        
        self.statusbar=QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.status=QLabel('DAYS')
        self.statusbar.addWidget(self.status)
        
        self.fileMenu=self.menuBar().addMenu('&File')
        self.load=self.fileMenu.addAction('Load')
        self.save=self.fileMenu.addAction('Save')
        self.fileMenu.addSeparator()
        self.quit=self.fileMenu.addAction('Quit')
        
        self.quit.triggered.connect(app.quit)
        self.load.triggered.connect(self.loadA)
        self.save.triggered.connect(self.saveA)
        
        self.editMenu=self.menuBar().addMenu('&Edit')
        self.fastest=self.editMenu.addAction('Fastest')
        self.fast=self.editMenu.addAction('Fast')
        self.normal=self.editMenu.addAction('Normal')
        self.slow=self.editMenu.addAction('Slow')
        self.editMenu.addSeparator()
        self.settings=self.editMenu.addAction('Settings')
        
        self.fastest.triggered.connect(self.fastestA)
        self.fast.triggered.connect(self.fastA)
        self.normal.triggered.connect(self.normalA)
        self.slow.triggered.connect(self.slowA)
        self.settings.triggered.connect(self.settingsA)
        
        
        
        self.world=WorldLabel() if USE_GRAPHICS else World()
        if USE_GRAPHICS:
            self.setCentralWidget(self.world)
        self.adjustSize()        
        global world
        world=self.world
        self.gen=Generation(10)
        self.world.populate(self.gen)
        self.year=1
        self.day=1
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.doTurn)
        self.timer.start(1)
    
    def closeA(self):
        self.running=False
        print self.running  
    
    def closeEvent(self,event):
        self.closeA()

    def loadA(self):
        print 'Not implemented'
    
    def saveA(self):
        print 'Not implemented'
    
    def fastestA(self):
        global USE_GRAPHICS
        USE_GRAPHICS =False
        print 'changed to no graph'
        self.world.setParent(None)
        self.world=World()
        global world
        world=self.world
        self.timer.setInterval(0)
        
    def fastA(self):
        if not USE_GRAPHICS:
            self.changeToGraphics()
        self.timer.setInterval(0)
    
    def normalA(self):
        if not USE_GRAPHICS:
            self.changeToGraphics()
        self.timer.setInterval(100)
    
    def slowA(self):
        if not USE_GRAPHICS:
            self.changeToGraphics()
        self.timer.setInterval(500)
    
    def settingsA(self):
        print 'Not implemented yet'
    
    def changeToGraphics(self):
        global USE_GRAPHICS
        USE_GRAPHICS=True
        self.world=WorldLabel()
        self.setCentralWidget(self.world)
        global world
        world=self.world
    
    def doTurn(self):
        if self.day<200:
            for cre in world.creatures.values():
                cre.doTurn()
            for food in world.foods.values():
                pass
                #food.animate()
            if USE_GRAPHICS:
                world.update()
            self.status.setText('Year: {0:}         Day: {1:03d}  Total eaten: {2}'.format(self.year,self.day,self.highscore))
            self.day+=1
        else:
            self.highscore=self.gen.totalEaten()
            self.gen=self.gen.nextGeneration()
            self.world.removeEverything()
            self.world.populate(self.gen)
            self.year+=1
            self.day=1
    
               
if __name__ == '__main__':
    global world
    app=QApplication(sys.argv)
    mw=MainWindow()
    mw.show()
    import cProfile
    command = """app.exec_()"""
    cProfile.runctx( command, globals(), locals(), filename="ga.profile" )
    #app.exec_()
 
        
        
        
    #app.exec_()
    sys.exit()
    
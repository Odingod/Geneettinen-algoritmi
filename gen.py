# -*- coding: utf-8 -*-
'''
Pohjakoodia geneettisen algoritmin projektiin


Kehitysideoita:
pienempiä:
- tallennus/lataus (yksittäisen otuksen tai koko sukupolven)
- gui-härpäkkeitä (asetuksia, tilastoja ym.)
- asetuksia
    - otusten määrä ja tyyppi
    - ruoan määrä
    - kartan koko
    - vuoden pituus
    - genomin koko
    - algoritmi
- haju (otus 'haistaa' onko lähellä ruokaa)
- erilaisia ruoan asetteluita ja asetuksia 
    - määrä
    - onko ruoan määrä aina sama (eli ilmestyykö uutta kun vanhaa syödään)
    - ruokaa vain tietyillä alueilla
    - ruoka on ryppäissä
- DONE vesi,seinät,
- DONE kartan generointia, karttaeditori tai kartan tuonti kuvasta
- kartassa useampia tasoja
- lentävät otukset
- uivat otukset(joita rannoilla kävelevät syövät)
- DONE vesi(erikseen uinti ja kävely eteenpäin)
- erilaiset ruoat(hidastaa, pysäyttää, sekoittaa, ym.)
- toisia otuksia syövät otukset (oma Generation)
- samassa maailmassa kaksi eri sukupolvea jotka kehittyvät eri algoritmeilla
- eri algoritmeja

isompia:
- parempi algoritmi
- pieni skriptikieli jolla voisi kirjoitella omia otuksia
- sen sijaan että optimoitaisiin yksittäisen otuksen fitnessiä, vertailtaisiin sukupolvia ja valittaisiin jatkoon se joka söi yhteensä eniten
- voisi yrittää saada olioita tekemään jotain yksinkertaisia tehtäviä esim. kuljeta esineitä 'pesään', ole tietyllä alueella. Näissä pitäisi keksiä miten oliot pisteytetään.
- otusten välinen kommunikointi(lähetä oma tila)
- hiiriohjaus
    - DONE ruokaa tähän 
    - näytä olion tiedot
    - siirrä oliota
    - zoomaus
    - ym.

   
'''
'''
Created on Jun 16, 2011

@author: anttir
'''
import sys, time

from PySide.QtCore import *
from PySide.QtGui import *
from random import randint
from random import choice
import csv

#from creature import *#Creature, CreatureLabel, Generation
from world import *
from food import *
from globals import *
import terrain
import io
from statisticsWindow import *
#import creature



class MainWindow(QMainWindow):   
    def __init__(self):
        self.running = True
        self.highscore = 0
        QMainWindow.__init__(self)   
        self.setWindowTitle('Geneettinen algoritmi')  

        self.mousePos = (0, 0)
        
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.status = QLabel('DAYS')
        self.statusbar.addWidget(self.status)
        
        self.fileMenu = self.menuBar().addMenu('&File')
        self.load = self.fileMenu.addAction('Load')
        self.save = self.fileMenu.addAction('Save')
        self.fileMenu.addSeparator()
        self.quit = self.fileMenu.addAction('Quit')
        
        self.quit.triggered.connect(app.quit)
        self.load.triggered.connect(self.loadA)
        self.save.triggered.connect(self.saveA)
        
        self.editMenu = self.menuBar().addMenu('&Edit')
        self.fastest = self.editMenu.addAction('Fastest')
        self.fast = self.editMenu.addAction('Fast')
        self.normal = self.editMenu.addAction('Normal')
        self.slow = self.editMenu.addAction('Slow')
        self.pause = self.editMenu.addAction('Pause')
        self.editMenu.addSeparator()
        self.settings = self.editMenu.addAction('Settings')
        
        self.statisticMenu = self.menuBar().addMenu('&Statistics')
        self.showStatistics = self.statisticMenu.addAction('Show statistics')
        self.exportStatistics = self.statisticMenu.addAction('Export statistics')
        
        self.showStatistics.triggered.connect(self.showStatisticsA)
        self.exportStatistics.triggered.connect(self.exportStatisticsA)
        
        self.fastest.triggered.connect(self.fastestA)
        self.fast.triggered.connect(self.fastA)
        self.normal.triggered.connect(self.normalA)
        self.slow.triggered.connect(self.slowA)
        self.pause.triggered.connect(self.pauseA)
        self.settings.triggered.connect(self.settingsA)
        self.terrainGenerator = terrain.NoiseMapGenerator(width=WIDTH+1, height=HEIGHT+1)
        #self.terrainGenerator = terrain.DrunkardTerrainGenerator(width=WIDTH+1, height=HEIGHT+1)
        
        
        self.world = WorldLabel() if USE_GRAPHICS else World(False)
        if USE_GRAPHICS:
            self.setCentralWidget(self.world)
        self.adjustSize()        
        self.paused=False
        self.makeNewTerrain(terrainGenerator=self.terrainGenerator)
        self.gen = Generation(10,self.world)
        self.world.populate(self.gen)
        self.year = 1
        self.day = 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.doTurn)
        self.timer.start(1)
        self.statWindow=None
        self.AddFoodAct = QAction("&Add food",self,
                                  statusTip="Add food to location",
                                  triggered=self.AddFood)
        self.whatsHereAct = QAction(
                "&Whats Here?", self,
                statusTip="Click to see whats under cursor!", 
                triggered=self.whatsHere)

        self.saveCreatureToFileAct = QAction("&Save creature", self,
                                             statusTip="Save creature to modify it",
                                             triggered=self.saveCreatureToFile)

        self.releaseCreatureAct = QAction("&Release creature", self,
                                          statusTip="Release creature",
                                          triggered=self.releaseCreature)
                                          
                                          
        #stats
        self.statEaten = []
        self.statWalked = []
        self.statAverageEaten = []
        self.statAverageWalked = []
        self.maximum = 0
        self.totalEaten = 0
        self.totalWalked= 0
        self.average=0.0
                
    def showStatisticsA(self, Statistics=None):
        if not self.statWindow:
            self.statWindow=StatisticsWindow(self)
            self.statWindow.show()
            
    def closeStatWindow(self):
        self.statWindow=None
        
    def exportStatisticsA(self,statistics=None):
        if self.statWindow:
            self.statWindow.exportStats()
        else:
            StatisticsWindow(self).exportStats()
		    
    def getStatisticString(self):
        string = ""
        i = 1
        for i in range(len(self.statEaten)):
            string += "year: " + str(i+1) + "\n"
            string += "Total eaten : " + str(self.statEaten[i]) + "\n" 
            string += "Total walked :" + str(self.statWalked[i])
            string += "\n"
            string += "\n"
        return string


    def contextMenuEvent(self, event):
        pos = QCursor.pos()
        pos = self.mapFromGlobal(pos)
        loc = pos.toTuple()
        
        h = self.size().height()
        w = self.size().width()
        location = (loc[0] / GRIDSIZE, loc[1] / GRIDSIZE - 2)
        self.mousePos = location

        menu = QMenu(self) 
        
        self.DockAct = QAction("&Open cmd", self, triggered = self.showdoc)
        
        self.PauseAct = QAction("&Pause",self,
                statusTip="Pause algorithm",
                triggered=self.pauseA)
        
        self.SlowAct = QAction("&Slow", self,
                statusTip="Set mode for Slow",
                triggered=self.slowA)
        
        
        self.NormalAct = QAction("&Normal", self,
                statusTip="Set mode for Normal",
                triggered=self.normalA)
        
        self.FastAct = QAction("&Fast", self,
                statusTip="Set mode for Fast",
                triggered=self.fastA)
        
        self.FastestAct = QAction("&Fastest", self,
                statusTip="Set mode for Fastest",
                triggered=self.fastestA)
           

        self.saveCreatureToFileAct = QAction("&Save creature", self,
                                             statusTip="Save creature to modify it",
                                             triggered=self.saveCreatureToFile)

        self.releaseCreatureAct = QAction("&Release creature", self,
                                          statusTip="Release creature",
                                          triggered=self.releaseCreature)

        
        SpeedMenu = menu.addMenu("&Mode")
        SpeedMenu.addAction(self.PauseAct)
        SpeedMenu.addAction(self.SlowAct)    
        SpeedMenu.addAction(self.NormalAct)
        SpeedMenu.addAction(self.FastAct)
        SpeedMenu.addAction(self.FastestAct)
        menu.addAction(self.AddFoodAct)
        menu.addAction(self.whatsHereAct)
        menu.addAction(self.DockAct)
        menu.addAction(self.saveCreatureToFileAct)
        menu.addAction(self.releaseCreatureAct)
        
        menu.exec_(event.globalPos())

    def makeNewTerrain(self, terrainGenerator=None, filename=None):
        """
        Luo uuden maaston, mutta ei uutta maailmaa
        Arguments:
        - `terrainGenerator`: which terrainGenerator you want to use
        - `filename`: if you want to load terrain from file, specify it here
        - If you specify both filename and terrainGenerator, terrain will be loaded
        from file
        """
        if filename is None and isinstance(terrainGenerator, terrain.DrunkardTerrainGenerator) or isinstance(terrainGenerator, terrain.NoiseMapGenerator):
            self.world.makeTerrain(terrainGenerator)

        elif isinstance(filename, str):
            self.world.loadTerrain(filename)

    def AddFood(self):

        location = self.mousePos
        print location
        if not self.world.USE_GRAPHICS:
            self.world.addFood(Food(location))
        else:
            self.world.addFood(FoodLabel(self.world, location), rando=False)


        
    def whatsHere(self):

        location = self.mousePos
        if self.world.getFood(location):
            print "food"
        elif self.world.getCreature(location):
            print "creature"
        print location
        
    def saveCreatureToFile(self):
        location = self.mousePos
        creature = self.world.getCreature(location)
        if creature:
            self.saveA({location: creature})

        else:
            print "Missed me HAHAHA >:D"

    def releaseCreature(self):
        location = self.mousePos
        self.loadA(clearFirst=False, location=location)

    def closeA(self):
        self.running = False
        print self.running  
    
    def closeEvent(self, event):
        self.closeA()

    def loadA(self, clearFirst=True, location=None):
        dialog = QFileDialog(self, caption="Load creatures")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("XML (*.xml)")
        dialog.setViewMode(QFileDialog.Detail)
        filename = ""
        if dialog.exec_():
            filename = dialog.selectedFiles()

        if filename == "" or filename is None:
            pass
        elif filename[0]:
            with open(filename[0], 'r') as f:
                if clearFirst:
                    self.world.removeCreatures()

                io.xmlToCreatures(filename[0], self.world, location)
                print "new creatures loaded"
                
                
    def saveA(self, creaturesToSave=None):
        dialog = QFileDialog(self, "Save creatures","creatures.xml")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter("XML (*.xml)")
        dialog.setDefaultSuffix(u'xml')
        dialog.setViewMode(QFileDialog.Detail)
        filename = ""

        if dialog.exec_():
            filename = dialog.selectedFiles()

        if filename == "" or filename is None:
            pass
        elif filename[0]:
            with open(filename[0], 'w') as f:
                if creaturesToSave is None:
                    io.creaturesToXML(self.world.creatures, filename[0])
                else:
                    io.creaturesToXML(creaturesToSave, filename[0])

                print "Creature(s) saved to", filename
    
    def fastestA(self):
        self.paused=False
        if not self.world.USE_GRAPHICS:
            return
        global USE_GRAPHICS
        USE_GRAPHICS = False
        print 'changed to no graph'
        self.world=self.world.changeToWorld()
        creatures=[]
        for cre in self.world.creatures:
            creatures.append(self.world.creatures[cre])
        self.gen=Generation(self.gen.size,self.world,creatures)
        self.setCentralWidget(None)
        self.timer.setInterval(0)
        
    def fastA(self):
        self.paused=False
        if not self.world.USE_GRAPHICS:
            self.changeToGraphics()
        self.timer.setInterval(0)
    
    def normalA(self):
        self.paused=False
        if not self.world.USE_GRAPHICS:
            self.changeToGraphics()
        self.timer.setInterval(100)
    
    def slowA(self):
        self.paused=False
        if not self.world.USE_GRAPHICS:
            print "changed"
            self.changeToGraphics()
        self.timer.setInterval(500)
    
    def pauseA(self):
        self.paused=True
    
    def settingsA(self):
        print 'Not implemented yet'
    
    def changeToGraphics(self):
        global USE_GRAPHICS
        USE_GRAPHICS = False
        self.world=self.world.changeToWorldLabel(self)
        creatures=[]
        for cre in self.world.creatures:
            creatures.append(self.world.creatures[cre])
        self.gen=Generation(self.gen.size,self.world,creatures)
        self.world.update()

    
    def doTurn(self):
        if self.paused:
            return
        if self.day < 200:
            for cre in self.world.creatures.values():
                cre.doTurn()

            for food in self.world.foods.values():
                pass
                # food.animate()

            if self.world.USE_GRAPHICS:
                self.world.update()
                #realtime stats
                self.highscore=self.gen.totalEaten()
                self.status.setText('Year: {0:}         Day: {1:03d}  Total eaten: {2:03d}  Maximum: {3:03d} Average: {4:03d}'\
                                        .format(self.year, self.day, self.highscore, self.maximum, int(self.average)))

            self.day += 1
        else:
            self.statEaten.append(self.gen.totalEaten())
            self.statWalked.append(self.gen.totalWalked())
            self.totalEaten += self.statEaten[-1]
            self.totalWalked+= self.statWalked[-1]
            if self.gen.totalEaten() > self.maximum: 
            	self.maximum = self.gen.totalEaten()

            self.statAverageEaten.append(self.totalEaten / self.year)
            self.statAverageWalked.append(self.totalWalked / self.year)
            self.average=self.statAverageEaten[-1]
            self.highscore = self.statEaten[-1]
            self.gen = self.gen.nextGeneration()
            self.world.removeEverything()
            self.world.populate(self.gen)
            self.year += 1
            self.day = 1
            self.status.setText('Year: {0:}         Day: {1:03d}  Total eaten: {2:03d}  Maximum: {3:03d} Average: {4:03d}'\
                                        .format(self.year, self.day, self.highscore, self.maximum, int(self.average)))
            if self.statWindow:
                self.statWindow.dataChanged()
                self.statWindow.draw()
           
    def exec_comand_string(self, string):
        if len(string) <= 0:
                return ""
        if string[0] != '/':
            return "Command must start with '/'\n"
        string = string[1:]
        
        Parts = string.split(' ')
        command = Parts[0]
        Args = Parts[1:]
        
        
        
        if command == "help":
            return self.prthelp()
            
        elif command == "quit":
            app.quit()
            
        elif command == "addfood":
            try:
                self.world.addFood(Food((int(Args[0]), int(Args[1]))) if not USE_GRAPHICS else FoodLabel(self, (int(Args[0]), int(Args[1]))))
            except:
                return "Unknown parameters in command" +string
        
        elif command == "addcreature":
            try:
                heading = None
                if Args[2] == "NORTH":
                    heading = (0, -1)
                elif  Args[2] == "EAST":
                    heading  = (1, 0)
                elif Args[2] == "SOUTH":
                    heading = (0, 1)
                elif Args[2] == "WEST":
                    heading = (-1, 0)
                else:
                    return "Unknown parameters in command" +string
                
                if len(Args) == 3:

                    creature = Creature((int(Args[0]), int(Args[1]), heading, self.world))
                    self.world.addCreature(creature)
                elif len(Args) == 4:
                    creature = Creature((int(Args[0]), int(Args[1])), heading, self.world, Args[4])
                    self.world.addCreature(creature)
            except:
                return "Unknown parameters in command" + string
        else:
            return "Unknown command " + command
    
    
    
    def prthelp(self):
        return ("Available commands:\n"
                "/help                          | Prints available commands and instructions to use commandline.\n"\
                "/quit                          | Shuts down gen.py.\n"
                "/addfood x y                   | Adds food to given location. Parameters x and y must be integers in range (0, 40).\n"
                "/deleteall                     | Erases every object from the map.\n"
                "/addcreature x y heading genome| Adds new creature defined by given genome to location (x, y) with heading towards given parameter.\n"
                "                               | Given genome must be proper tuple as defined in creature constructor or genome can be given as a empty parameter,\n"
                "                               | thus genome is constructed by random. Heading must be one of the following: NORTH, EAST, SOUTH, WEST.\n")
                                               
        
    def showdoc(self):
        self.cmd=Cmd(self)
        
    
class Cmd(QWidget):
    def __init__(self, parent=None):
        super(Cmd, self).__init__(parent)
        super(Cmd, self).setWindowFlags(Qt.Window)
        self.commands = []
        self.currentcommand = 0
        self.parent = parent
        self.commandList = QListWidget(self)
        self.commandList.addItem(parent.prthelp())
        self.input = QLineEdit(self)
        self.button = QPushButton("&Enter", self)
        self.button.clicked.connect(self.button_click_event)
        
        
        layout = QVBoxLayout()
        layout.addWidget(self.commandList)
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
        self.show()
        
    def button_click_event(self):
        self.commandList.addItem(self.input.text())
        self.commands[len(self.commands)]=self.input.text()
        self.commands.append("")
    
        text = self.parent.exec_comand_string(self.input.text())
        self.commandList.addItem(text)
        self.input.setText("")
        self.currentcommand = len(self.commands)
    def keyPressEvent(self, event):
        if event.key() == 16777220:
            self.commandList.addItem(self.input.text())
            self.commands.append("")
            self.commands[len(self.commands)-1]=self.input.text()
            text = self.parent.exec_comand_string(self.input.text())
            self.commandList.addItem(text)
            self.input.setText("")
            self.currentcommand = len(self.commands)
        if event.key() == 16777235:
            self.currentcommand -=1
            self.currentcommand = self.currentcommand % len(self.commands)
            self.input.setText(self.commands[self.currentcommand])
        if event.key()  == 16777237:
            self.currentcommand -=1
            self.currentcommand = self.currentcommand % len(self.commands)
            self.input.setText(self.commands[self.currentcommand])
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    import cProfile
    command = """app.exec_()"""
    cProfile.runctx(command, globals(), locals(), filename="ga.profile" )
    #app.exec_()
               
    sys.exit()
    

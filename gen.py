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
import csv

#from creature import *#Creature, CreatureLabel, Generation
from world import *
from food import *
from globals import *
import terrain
#import creature

import sys, time

class MainWindow(QMainWindow):   
    def __init__(self):
        self.running = True
        self.highscore = 0
        QMainWindow.__init__(self)     
        
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
        self.editMenu.addSeparator()
        self.settings = self.editMenu.addAction('Settings')
        
        self.statisticMenu = self.menuBar().addMenu('&Statistics')
        self.showstatistics = self.statisticMenu.addAction('Show statistics')
        self.exportstatistics = self.statisticMenu.addAction('Export statistics')
        
        self.showstatistics.triggered.connect(self.showstatisticsA)
        self.exportstatistics.triggered.connect(self.exportA)
        
        self.fastest.triggered.connect(self.fastestA)
        self.fast.triggered.connect(self.fastA)
        self.normal.triggered.connect(self.normalA)
        self.slow.triggered.connect(self.slowA)
        self.settings.triggered.connect(self.settingsA)
        self.terrainGenerator = terrain.NoiseMapGenerator(width=WIDTH+1, height=HEIGHT+1)
        #self.terrainGenerator = terrain.DrunkardTerrainGenerator(width=WIDTH+1, height=HEIGHT+1)
        
        
        self.world = WorldLabel() if USE_GRAPHICS else World()
        if USE_GRAPHICS:
            self.setCentralWidget(self.world)
        self.adjustSize()        
        global world
        world = self.world
        self.genret = WorldRetriever(world)
        self.makeNewTerrain(terrainGenerator=self.terrainGenerator)
        self.gen = Generation(10)
        self.world.populate(self.gen)
        self.year = 1
        self.day = 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.doTurn)
        self.timer.start(1)
        self.AddFoodAct = QAction("&Add food",self,
                                  statusTip="Add food to location",
                                  triggered = self.AddFood)
        self.whatsHereAct = QAction(
                "&Whats Here?", self,
                statusTip="Click to see whats under cursor!", 
                triggered= self.whatsHere)
                
    def showstatisticsA(self, Statistics=None):
        QMessageBox.information(self,"Statistics",
                                self.getStatisticString(),
                                QMessageBox.Ok)
        
    def exportA(self,statistics=None):
        filename = QFileDialog.getSaveFileName(self, "Save as .csv",
                                               filter = ("CSV (*.csv)"))
        if filename[0]:
            with open(filename[0], 'wb') as f:
                w = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONE)
                w.writerow(["Total Eaten:", "Total Walked:"])
                for stat in world.statistics:
                    w.writerow([stat.totaleaten, stat.totalwalked])
		    
    def getStatisticString(self):
        string = ""
        i = 1
        for stat in world.statistics:
            string += "year: " + str(i) + "\n"
            string += "Total eaten : " + str(stat.totaleaten) + "\n" 
            string += "Total walked :" + str(stat.totalwalked)
            string += "\n"
            string += "\n"
            i += 1
        return string


    def contextMenuEvent(self, event):
        
        menu = QMenu(self) 
        
        self.DockAct = QAction("&Open cmd", self, triggered = self.showdoc)
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
           
        
        SpeedMenu = menu.addMenu("&Mode")
        
        SpeedMenu.addAction(self.SlowAct)    
        SpeedMenu.addAction(self.NormalAct)
        SpeedMenu.addAction(self.FastAct)
        SpeedMenu.addAction(self.FastestAct)
        menu.addAction(self.AddFoodAct)
        menu.addAction(self.whatsHereAct)
        menu.addAction(self.DockAct)
        
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
            world.makeTerrain(terrainGenerator)

        elif isinstance(filename, str):
            world.loadTerrain(filename)

    def AddFood(self):
        
        #Toi sijainnin haku kusee viel vahasen.
        pos = QCursor.pos()
        pos =self.mapFromGlobal(pos)
        loc = pos.toTuple()
        
        h = self.size().height()
        w = self.size().width()
        location = int(loc[0] * HEIGHT / h) - 3, int(loc[1] * WIDTH / w - 3)
        world.addFood(Food(location) if not USE_GRAPHICS else FoodLabel(self, location))
        print "food added"
        
    def whatsHere(self):
        pos = QCursor.pos()
        pos =self.mapFromGlobal(pos)
        loc = pos.toTuple()
        
        h = self.size().height()
        w = self.size().width()
        location = int(loc[0] * HEIGHT / h) - 3, int(loc[1] * WIDTH / w - 3)
        
        if world.getFood(location):
            print "food"
        elif world.getCreature(location):
            print "creature"
        print location
        

    def closeA(self):
        self.running = False
        print self.running  
    
    def closeEvent(self, event):
        self.closeA()

    def loadA(self):
        print 'Not implemented'
    
    def saveA(self):
        print 'Not implemented'
    
    def fastestA(self):
        global USE_GRAPHICS
        USE_GRAPHICS = False
        print 'changed to no graph'
        self.world.setParent(None)
        self.world = World()
        global world
        world = self.world
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
        USE_GRAPHICS = True
        self.world=WorldLabel()
        self.setCentralWidget(self.world)
        global world
        world = self.world
    
    def doTurn(self):
        if self.day < 200:
            for cre in world.creatures.values():
                cre.doTurn()

            for food in world.foods.values():
                pass
                #food.animate()

            if USE_GRAPHICS:
                world.update()
                self.status.setText('Year: {0:}         Day: {1:03d}  Total eaten: {2}  Maximum: {3:03d} Average: {4:03d}'\
                                        .format(self.year, self.day, self.highscore, world.maximum, int(world.average)))

            self.day += 1

        else:
            stat = Statistics(self.gen.totalEaten(), self.gen.totalWalked())
            world.total += self.gen.totalEaten()

            if self.gen.totalEaten() > world.maximum: 
            	world.maximum = self.gen.totalEaten()

            world.average = world.total / self.year
            world.statistics.append(stat)
            self.highscore = self.gen.totalEaten()
            self.gen = self.gen.nextGeneration()
            self.world.removeEverything()
            self.world.populate(self.gen)
            self.year += 1
            self.day = 1
    
    
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
                world.addFood(Food((int(Args[0]), int(Args[1]))) if not USE_GRAPHICS else FoodLabel(self, (int(Args[0]), int(Args[1]))))
            except:
                return "Unknown parameters in command" +string
        
        elif command == "addcreature":
            try:
                heading = None
                if Args[2] == "NORTH":
                    heading = (0, -1)
                elif  Args[2] == "EAST":
                    heading  = (1, 0)
                elif Args[2] =="SOUTH":
                    heading = (0, 1)
                elif Args[2] == "WEST":
                    heading = (-1, 0)
                else:
                    return "Unknown parameters in command" +string
                
                if len(Args)==3:

                    creature = Creature((int(Args[0]), int(Args[1]), heading))
                    world.addCreature(creature)
                elif len(Args)==4:
                    creature = Creature((int(Args[0]), int(Args[1]), heading), Args[4])
                    world.addCreature(creature)
            except:
                return "Unknown parameters in command" +string
        else:
            return "Unknown command "+command
    
    
    
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
    global world
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    import cProfile
    command = """app.exec_()"""
    cProfile.runctx(command, globals(), locals(), filename="ga.profile" )
    #app.exec_()
               
    sys.exit()
    

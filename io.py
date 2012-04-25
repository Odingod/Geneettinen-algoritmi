# -*- coding: utf-8 -*-
import datetime
import sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom

import png

import globals
import creature

def transpose(arry):
    """
    Arguments:
    - `array to transpose`:
    Returns:
    transposed array
    """
    return [map(lambda li: li[i], arry) for i in range(len(arry[0]))]

def dateString():
    string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return string


def imageDataToArray(imageData):
    """
    Arguments:
    - `imageData`: image data
    Returns:
    Array of map-data
    """
    iRED = 0
    iGREEN = 1
    iBLUE = 2
    iWIDTH = 0
    iHEIGHT = 1
    iCOLORDATA = 2

    xlen = imageData[iWIDTH] * 3  # r, g and b for each pixel
    ylen = imageData[iHEIGHT]
    colorData = imageData[iCOLORDATA]
    arry = [[0] * (xlen / 3) for y in xrange(ylen)]

    for y in xrange(ylen):
        row = colorData.next()
        for x in xrange(0, xlen, 3):
            rgb = [-1, -1, -1]
            for i in (iRED, iGREEN, iBLUE):
                rgb[i] = row[x + i]
            ID = globals.getAssociatedID(tuple(rgb))
            arry[y][x / 3] = ID

    arry = transpose(arry)

    return arry


def mapFileToArray(filename):
    """
    Use this function to open map data and convert it to array of map-data
    Arguments:
    - `filename`: map-image to open
    Returns:
    Array of map-data
    Example:
    terrain = io.mapFileToArray("omaMappiJee.png")
    """
    # try:
    f = open(filename, 'rb')
    pngReader = png.Reader(filename=filename)
    imageData = pngReader.asRGB()
    arry = imageDataToArray(imageData)
    f.close()
    # except:
    #     print "ERROR: problem reading file"
    #     print "Perhaps it's missing or you are trying to open non-png file?"

    # imageData = mapFileToImageData(file)
    # arry = colorDataToArray(imageData)
    
    return arry


def arrayToColorData(arry):
    """
    Constructs colorData-array from map-data-array.

    Arguments:
    - `arry`: Two-dimensional array of blocks
    Returns:
    Color-data which can be saved to image file
    """
    transposedArray = transpose(arry)
    xlen = len(transposedArray[0]) * 3
    ylen = len(transposedArray)
    colorData = [[0] * xlen for y in xrange(ylen)]

    for y in xrange(ylen):
        for x in xrange(0, xlen, 3):
            rgb = globals.getAssociatedRGB(terrainID=transposedArray[y][x / 3])
            for i in xrange(3):
                # print "RGB:", rgb
                # print " at y, x + i: ", colorArray[y]
                colorData[y][x + i] = rgb[i]

    return colorData


def colorDataToMapFile(colorData, filename):
    """
    Arguments:
    - `colorData`:
    - `filename`: name of file where you want to save map
    """
    mapWidth = len(colorData[0]) / 3
    mapHeight = len(colorData)

    try:
        f = open(filename, 'wb')
        pngWriter = png.Writer(width=mapWidth, height=mapHeight)
        pngWriter.write(f, colorData)
        f.close()

    except:
        print "ERROR writing to file", filename


def arrayToFile(arry, filename=""):
    """
    This is a helper function to save terrain-data to image file
    Arguments:
    - `arry`: Array of terrain-data
    - `filename`: name of file where you want to save map
    Returns:
    Nothing
    Example:
    io.arrayToFile(terrain, "omaMappiJee.png")
    Output:
    image-file, which you can load back to array with
    mapFileToArray-function
    """
    if filename == "":
        filename += "map-"
        filename += dateString()
        filename += ".png"
    colorData = arrayToColorData(arry)
    colorDataToMapFile(colorData, filename)

def creaturesToXML(creatures, filename=""):
    """
    
    Arguments:
    - `creatures`: List of creatures object
    - `filename`: Filename. If omitted, function will generate it's own name
    """

    root = Element("creatures")
    for cre in creatures.values():
        cElement = SubElement(root, "creature")
        
        loc = SubElement(cElement, "location")
        x = SubElement(loc, "x")
        x.text = str(cre.loc[0])
        y = SubElement(loc, "y")
        y.text = str(cre.loc[1])
        
        heading = SubElement(cElement, "heading")
        hx = SubElement(heading, "x")
        hx.text = str(cre.heading[0])
        hy = SubElement(heading, "y")
        hy.text = str(cre.heading[1])

        sight = SubElement(cElement, "sight")
        sight.text = str(cre.sight)

        memory = SubElement(cElement, "memory")
        memory.text = str(cre.memory)

        calories = SubElement(cElement, "calories")
        calories.text = str(cre.calories)
        
        walked = SubElement(cElement, "walked")
        walked.text = str(cre.walked)

        eaten = SubElement(cElement, "eaten")
        eaten.text = str(cre.eaten)
        
        accessible = SubElement(cElement, "accessibleTerrain")
        for tType in cre.accessibleTerrain:
            terrain = SubElement(accessible, "type")
            terrain.text = tType

        genome = SubElement(cElement, "genome")
        for mem in cre.genome:
            mElement = SubElement(genome, "memory")
            for pair in mem:
                pElement = SubElement(mElement, "pair")
                action = SubElement(pElement, "action")
                action.text = str(pair[0])
                somethingIDontKnow = SubElement(pElement, "something")
                somethingIDontKnow.text = str(pair[1])
                
        
    raw = ElementTree.tostring(root)
    parsed = minidom.parseString(raw)
    parsed = parsed.toprettyxml(indent="  ")

    if filename == "":
        filename += "creatures-"
        filename += dateString()
        filename += ".xml"

    f = open(filename, 'w')
    f.write(parsed)
    f.close()


def xmlToCreatures(filename, world, location=None):
    """
    
    Arguments:
    - `filename`: Name of the XML that contains creatures
    - `world`: world where function should insert creatures
    
    Returns dictionary of creatures
    """
    creatures = {}

    tree = ElementTree.ElementTree()
    tree.parse(filename)

    root = tree.getroot()

    creatureElems = root.findall("creature")

    # e as prefix means element in XML

    for cre in creatureElems:
        loc = None
        if location is None:
            eLoc = cre.find("location")
            eLocX = eLoc.find("x")
            eLocY = eLoc.find("y")
            xLoc = int(eLocX.text)
            yLoc = int(eLocY.text)
        
            loc = (xLoc, yLoc)

        else:
            loc = location

        eHeading = cre.find("heading")
        eHeadingX = eHeading.find("x")
        eHeadingY = eHeading.find("y")
        xHeading = int(eHeadingX.text)
        yHeading = int(eHeadingY.text)

        heading = (xHeading, yHeading)

        eSight = cre.find("sight")
        sight = int(eSight.text)

        eMem = cre.find("memory")
        mem = int(eMem.text)

        eTerrTypes = cre.find("accessibleTerrain")
        terrainTypes = []
        for eT in eTerrTypes:
            terrainTypes.append(eT.text)

        eGenome = cre.find("genome")
        eGenomeMemories = eGenome.findall("memory")
        genome = []
        for eGMem in eGenomeMemories:
            ePairs = eGMem.findall("pair")
            memory = []
            for eP in ePairs:
                action = int(eP.find("action").text)
                something = int(eP.find("something").text)
                memory.append((action, something))

            genome.append(memory)

        eCalories = cre.find("calories")
        calories = int(eCalories.text)

        eWalked = cre.find("walked")
        walked = int(eWalked.text)

        eEaten = cre.find("eaten")
        eaten = int(eEaten.text)

        creatureObj = creature.CreatureLabel(world, loc, genome)
        creatureObj.sight = sight
        creatureObj.memory = mem
        creatureObj.walked = walked
        creatureObj.accessibleTerrain = terrainTypes
        creatureObj.eaten = eaten
        creatureObj.calories = calories

        world.addCreature(creatureObj, rando=False)
        
    return creatures


if __name__ == '__main__':
    terrain = mapFileToArray("otus.png")
    arrayToFile(terrain, "testiotus.png")

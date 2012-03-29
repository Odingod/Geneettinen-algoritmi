# -*- coding: utf-8 -*-
import png
import globals
import datetime

def transpose(arry):
    """
    Arguments:
    - `array to transpose`:
    Returns:
    transposed array
    """
    return [map(lambda li: li[i], arry) for i in range(len(arry[0]))]


# def mapFileToImageData(filename):
#     """
#     Arguments:
#     - `filename`:
#     Returns:
#     Color-data from map-file
#     """
#     try:
#         f = open(filename, 'rb')
#         pngReader = png.Reader(file=f)
#         imageData = pngReader.asRGB()
#         f.close()
#         return imageData
#     except:
#         print "ERROR: problem reading file"
#         print "Perhaps it's missing or you are trying to open non-png file?"

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
        filename += datetime.datetime.now().isoformat().replace(".", "-").replace(":", "-")
        filename += ".png"
    colorData = arrayToColorData(arry)
    colorDataToMapFile(colorData, filename)

if __name__ == '__main__':
    terrain = mapFileToArray("otus.png")
    arrayToFile(terrain, "testiotus.png")

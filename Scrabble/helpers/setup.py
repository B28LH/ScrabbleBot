import numpy as np

from helpers import data


def ValidNear(xC, yC, width):
    t = [(xC + x[0], yC + x[1]) for x in data.AddOn]
    return [x for x in t if 0 <= x[0] < width and 0 <= x[1] < width]


def ValidVert(xC, yC, width):
    return [x for x in ((xC + 1, yC), (xC - 1, yC)) if 0 <= x[0] < width and 0 <= x[1] < width]


def ValidHorz(xC, yC, width):
    return [x for x in ((xC, yC + 1), (xC, yC - 1)) if 0 <= x[0] < width and 0 <= x[1] < width]


def AlphaArray(arr):
    return np.isin(arr, data.alphabet).astype(int)


def initialise(GameName, WWF=False, Small=False):
    if WWF:
        dictfile = 'wwf.txt'
        allTileBonus = 35
        startTile = False
        tileValues = data.wTileValues
        if Small:
            design = data.friendsSmall
        else:
            design = data.friendsBig
    else:
        dictfile = 'scra.txt'
        allTileBonus = 50
        startTile = True
        tileValues = data.sTileValues
        design = data.friendsBig

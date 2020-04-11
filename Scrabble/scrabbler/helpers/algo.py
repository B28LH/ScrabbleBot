"""The brains of the scrabble bot
"""

import numpy as np
from itertools import permutations
from scrabbler.helpers import data
from scipy import ndimage


def posMove(row, col, across=True):  # Positive is up or left -- MAKE A GENERATOR
    if across:
        if col > 0:
            return row, col - 1
    elif row > 0:
        return row - 1, col
    return False


def negMove(row, col, size, across=True):  # Negative is down or right
    if across:
        if col < size - 1:
            return row, col + 1
    elif row < size - 1:
        return row + 1, col
    return False


def betterMoveTiles(boardObj, across=True, both=False):
    """ Finds the playable squares from a board

    :param boardObj: a Board() Object
    :param across: whether checking for horizontal (across) or vertical borders
    :param both: whether both across and down are wanted for output (1 = Across, 2 = Down, 3 = Both)
    :return: an array of squares which satisfy border condition, and a list of those points
    """

    def leftRight(arr):
        return np.any(arr * np.r_[0, 0, 0, 1, 0, 1, 0, 0, 0])

    def upDown(arr):
        return np.any(arr * np.r_[0, 1, 0, 0, 0, 0, 0, 1, 0])

    def allFour(arr):
        return np.sum(np.unique(arr * np.r_[0, 1, 0, 2, 0, 2, 0, 1, 0]))

    Starters = np.where(boardObj.squares == '?', -1, 0)
    if np.any(Starters):
        return Starters, np.transpose(Starters.nonzero())
    if both:
        border = allFour
    elif across:
        border = leftRight
    else:
        border = upDown
    tileLoc = boardObj.AlphaArray()
    surround = ndimage.generic_filter(tileLoc, border, size=(3, 3), mode='constant')
    output = (1 - tileLoc) * surround
    return output, np.transpose(output.nonzero())


def completeWord(boardObj, coord, across=True):
    """ Finds longest line of letters from a spawn tile

    :param boardObj: a Board() Object
    :param coord: (row,col) of the spawn tile
    :param across: complete the word across (instead of down)
    :return: before, after, both strings, representing the contiguous tiles above/left and down/right
    """
    row, col = coord
    content = boardObj.AlphaArray()
    posPart = ''
    while True:
        tile = posMove(row, col, across)
        if tile and content[tile]:
            posPart += boardObj.squares[tile]
            row, col = tile
        else:
            break
    row, col = coord
    negPart = ''
    while True:
        tile = negMove(row, col, boardObj.size, across)
        if tile and content[tile]:
            negPart += boardObj.squares[tile]
            row, col = tile
        else:
            break
    return posPart[::-1], negPart


def crossChecks(boardObj):
    """ Produces all the valid vertically bordered cells

    :param boardObj:
    :return: outArray, a (NON NUMPY) array containing working letters for each square
    """
    outArray = [[None for _ in range(boardObj.size)] for _ in range(boardObj.size)]
    moveGird, moveList = betterMoveTiles(boardObj, across=False)
    for row, col in moveList:
        works = []
        before, after = completeWord(boardObj, (row, col), across=False)
        for char in data.loweralpha:
            newWord = char.join([before, after])
            if newWord in data.wordset:
                works.append(char)
        if len(works) > 0:
            outArray[row][col] = works
    return outArray


def botPlay(rack, boardObj):
    """ Plays the best move possible from a given rack

    :param rack: a string of the letters from the rack
    :param boardObj: a Board() object
    :return: TBD: MoveObj?
    """
    crossed = crossChecks(boardObj)
    anchorGrid, anchorList = betterMoveTiles(boardObj, both=True)  # IMPROVEMENT: just one betterMoveTiles.
    for anchorRow, anchorCol in anchorList:
        goodLetters = crossChecks[anchorRow][anchorCol]
        if goodLetters is not None:
            goodAnchors = set(rack) & set(goodLetters)  # Rack letters which can be played in the anchor
        else:
            goodAnchors = set(rack)
        before, after = completeWord(boardObj, (anchorRow, anchorCol))
        if before == '':
            left = posMove(anchorRow, anchorCol)
            counter = 0  # Counter is the number of free spaces you have to the left.
            while left and not anchorGrid[left]:
                left = posMove(left[0], left[1])
                counter += 1

        else:
            pass
        # Either 1) The anchor left borders a placed tile / wall OR we have free space

    pass

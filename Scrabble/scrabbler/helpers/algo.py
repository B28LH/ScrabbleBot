"""The brains of the scrabble bot
"""

import numpy as np
from itertools import permutations, chain
from scrabbler.helpers import data, core
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


def crossChecks(boardObj):  # TODO: make it returns a list of sets
    """ Produces an array of the valid one-tile down moves for each square

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


def checkWordMatches(startLen, word, anchorRow, anchorCol, remainingTiles, boardObj):  # TODO: Clean up the logic
    """ When given a word, checks that the word can be played given the board and tiles
        WORKING
    """
    if word not in data.wordset:  # This might not be needed
        return False
    i = startLen
    letters = list(remainingTiles)
    while i < len(word):  # Relative position to anchor
        myRow, myCol = anchorRow, anchorCol + i
        crossStatus = data.crossed[myRow][myCol]  # Crossed should be in data
        if crossStatus is None:
            theSquare = boardObj.squares[myRow][myCol]
            if theSquare.isalpha():  # Use alphaArray?
                if theSquare != word[i]:
                    return False
            elif word[i] not in letters:
                return False
            else:
                letters.remove(word[i])
        else:
            if word[i] not in crossStatus or word[i] not in letters:
                return False
            letters.remove(word[i])
        i += 1
    rightTile = posMove(anchorRow, anchorCol + i)
    if rightTile is not None and boardObj.AlphaArray()[rightTile]:  # Checks if right is not clear.
        return False
    return True


def botPlay(rack, boardObj):
    """ Plays the best move possible from a given rack

    :param rack: a string of the letters from the rack
    :param boardObj: a Board() object
    :return: TBD: MoveObj?
    """
    data.crossed = crossChecks(boardObj)
    anchorGrid, anchorList = betterMoveTiles(boardObj, both=True)  # TODO: IMPROVEMENT: just one betterMoveTiles.
    possibleMoves = []  # A list of Move() objects
    for anchorRow, anchorCol in anchorList:
        goodLetters = data.crossed[anchorRow][anchorCol]  # Checking the anchor square for down restrictions
        if goodLetters is not None:
            goodAnchors = set(rack) & set(goodLetters)  # Rack letters which can be played in the anchor
            if goodAnchors == {}:  # Can't play at this anchor
                continue  # Does this work to quit out of the for loop?
        else:
            goodAnchors = set(rack)
        before, after = completeWord(boardObj, (anchorRow, anchorCol))
        leftParts = []
        if before == '':
            left = posMove(anchorRow, anchorCol)
            counter = 0  # Counter is the number of free spaces you have to the left.
            while left and not anchorGrid[left]:
                left = posMove(left[0], left[1])
                counter += 1
        for anchorLetter in goodAnchors:  # going through each possible anchor
            tilesLeft = list(rack)
            tilesLeft.remove(anchorLetter)  # Remaining tiles on your rack
            if before == '':  # TODO: The logic here could be cleaned up a bit (double before)
                # This step could really blow up (around 2000 results), problematic IF COUNTER <1 ??
                tempLeftParts = chain.from_iterable([permutations(tilesLeft, i) for i in range(0, counter + 1)])
                # TODO: Clean up leftParts
                leftParts = [''.join((*part, anchorLetter, after)) for part in tempLeftParts]
                # what about having no left part???, is zero working?
            else:
                leftParts = [''.join((before, anchorLetter, after))]
            for start in leftParts:
                theseTilesLeft = list(tilesLeft)
                for char in start:
                    theseTilesLeft.remove(char)  # Now we know which tiles we have left to play.
                numUsedTiles = len(start)
                endings = data.completor(start)
                # Going to try all possible endings, rather than try all fittings
                # THIS IS A FORK IN THE ROAD FOR THE ALGO
                for word in endings:
                    if checkWordMatches(numUsedTiles, word, anchorRow, anchorCol, theseTilesLeft, boardObj):
                        # TODO: Check that start coordinates are good
                        possibleMoves.append(core.Move(word, (anchorRow, anchorCol - len(start) + 1), boardObj))

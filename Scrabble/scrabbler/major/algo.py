"""The brains of the scrabble bot
"""

import numpy as np
from itertools import permutations, chain
from scrabbler.major import data, core
from copy import deepcopy
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
    surround = ndimage.generic_filter(boardObj.alpha, border, size=(3, 3), mode='constant')
    output = (1 - boardObj.alpha) * surround
    return output, np.transpose(output.nonzero())


def completeWord(boardObj, coord, across=True):
    """ Finds longest line of letters from a spawn tile
    :param boardObj: a Board() Object
    :param coord: (row,col) of the spawn tile
    :param across: complete the word across (instead of down)
    :return: before, after, both strings, representing the contiguous tiles above/left and down/right
    """
    row, col = coord
    posPart = ''
    while True:
        tile = posMove(row, col, across)
        if tile and boardObj.alpha[tile]:
            posPart += boardObj.squares[tile]
            row, col = tile
        else:
            break
    row, col = coord
    negPart = ''
    while True:
        tile = negMove(row, col, boardObj.size, across)
        if tile and boardObj.alpha[tile]:
            negPart += boardObj.squares[tile]
            row, col = tile
        else:
            break
    return posPart[::-1], negPart


def crossChecks(boardObj):
    """ Produces an array of the valid one-tile down moves for each square

    :param boardObj:
    :return: outArray, a (NON NUMPY) array:
        1) If the cell is occupied by a letter, is None
        2) If the cell is not affected by any vertical collisions, is C (for clear)
        3) If the cell is affected by any vertical collisions, a set of valid tiles to place (CANNOT BE EMPTY)
        4) If the cell is affected by vertical collisions and no tile can be place, is I

    """
    outArray = [["C" for _ in range(boardObj.size)] for _ in range(boardObj.size)]
    moveGrid, _ = betterMoveTiles(boardObj, across=False)
    for row in range(boardObj.size):
        for col in range(boardObj.size):
            if moveGrid[row][col] and moveGrid[row][col] != -1:  # Checking for start squares
                works = set()
                before, after = completeWord(boardObj, (row, col), across=False)
                for char in data.loweralpha:
                    newWord = char.join((before, after))
                    if newWord in data.wordset:
                        works.add(char)
                if len(works) > 0:
                    outArray[row][col] = works
                else:
                    outArray[row][col] = "I"
            elif boardObj.alpha[row, col]:
                outArray[row][col] = None
    return outArray


def checkWordMatches(startLen, word, anchorRow, anchorCol, remainingTiles, boardObj):  # TODO: Clean up the logic
    """ When given a word, checks that the word can be played given the board and tiles
        WORKING
        BUG/FEATURE: DOESNT CHECK IF YOU HAVE THE LETTERS TO PLAY THE ANCHOR

    :param startLen: the index of the first non-anchored tile after the anchor
    :param word: the word you are playing
    :param anchorRow: anchored Row
    :param anchorCol: anchored Col
    :param remainingTiles: the tiles you can play with
    :param boardObj: the Board() object
    :return: True if the word can be played, false if not
    """
    if word not in data.wordset:  # This might not be needed
        return False
    elif anchorCol + len(word) - startLen >= boardObj.size:  # Check if the word will go over the board
        return False
    elif startLen == len(word):  # Letting two letter words be played
        return True
    elif data.crossed is None:  # For when the function is called on its own
        data.crossed = crossChecks(boardObj)
    i = startLen
    letters = list(remainingTiles)
    while i < len(word):  # Relative position to anchor
        myRow, myCol = anchorRow, anchorCol + 1 - startLen + i  # Finding i's position on the board
        crossStatus = data.crossed[myRow][myCol]  # Crossed should be in data
        if crossStatus is None:
            if boardObj.squares[myRow, myCol] != word[i]:
                return False
        elif crossStatus == "I":
            return False
        else:
            if crossStatus != "C" and word[i] not in crossStatus:
                return False
            elif word[i] not in letters:
                return False
            letters.remove(word[i])
        i += 1
    rightTile = negMove(anchorRow, anchorCol - startLen + len(word), boardObj.size)
    if rightTile is not None and boardObj.alpha[rightTile]:  # Checks if right is not clear.
        return False
    return True


def wrapCheckWord(start, extraStart, anchorRow, anchorCol, playableTiles, possibleMoves, boardObj, across=True):
    """ extraStart includes placed tiles to the right of the anchor, start does not"""
    endings = data.completor.keys(extraStart)
    startLen = len(start)
    for word in endings:
        if checkWordMatches(startLen, word, anchorRow, anchorCol, playableTiles, boardObj):
            if across:
                row, col = anchorRow, anchorCol - startLen + 1
            else:
                row, col = anchorCol - startLen + 1, anchorRow
            possibleMoves.append(core.Move(word, (row, col), boardObj, across=across, score=None))


def anchorCheck(anchorRow, anchorCol, rack):
    """ Checks to see if any tiles from rack can be played at the anchor

    :param anchorRow: row of anchor
    :param anchorCol: col of anchor
    :param rack: total tiles on rack
    :return: False, if no anchor can be played, or a set of possible plays
    """
    goodLetters = data.crossed[anchorRow][anchorCol]  # Checking the anchor square for down restrictions
    if goodLetters is None or goodLetters == "I":
        return False  # The anchor cannot be played, so move to next anchor spot
    elif goodLetters == "C":
        goodAnchors = set(rack)
    else:
        goodAnchors = set(rack) & set(goodLetters)  # Rack letters which can be played in the anchor
        if len(goodAnchors) == 0:  # Can't play at this anchor
            return False  # Does this work to quit out of the for loop?
    return goodAnchors


def moveOneWay(rack, boardObj, across):
    """ Plays the best move possible from a given rack

    :param rack: a string of the letters from the rack
    :param boardObj: a Board() object
    :param across: whether the bot is playing across moves
    :return: an array of Move() objects
    """
    data.crossed = crossChecks(boardObj)
    anchorGrid, anchorList = betterMoveTiles(boardObj, both=True)  # TODO: IMPROVEMENT: just one betterMoveTiles.
    possibleMoves = []  # A list of Move() objects
    for anchorRow, anchorCol in anchorList:
        goodAnchors = anchorCheck(anchorRow, anchorCol, rack)
        if not goodAnchors:
            continue  # No anchors to play, so move to next possible anchor
        before, after = completeWord(boardObj, (anchorRow, anchorCol), across=True)
        for anchorLetter in goodAnchors:  # going through each possible anchor
            tilesLeft = list(rack)
            tilesLeft.remove(anchorLetter)  # Remaining tiles on your rack
            if before == '':
                left = posMove(anchorRow, anchorCol)
                counter = 0  # Counter is the number of free spaces you have to the left.
                while left and not anchorGrid[left]:
                    left = posMove(left[0], left[1])
                    counter += 1
                # This step could really blow up (around 2000 results), problematic IF COUNTER <1 ??
                # The list thing also might blow up
                tempLeftParts = chain.from_iterable([permutations(tilesLeft, i) for i in range(0, counter + 1)])
                leftParts = [(part, ''.join((*part, anchorLetter, after))) for part in tempLeftParts]
                for initial, extraStart in leftParts:
                    theseTilesLeft = list(tilesLeft)
                    for char in initial:
                        theseTilesLeft.remove(char)
                    start = ''.join((*initial, anchorLetter))
                    wrapCheckWord(start, extraStart, anchorRow, anchorCol,
                                  theseTilesLeft, possibleMoves, boardObj, across=across)
            else:
                start = ''.join((before, anchorLetter))
                extraStart = ''.join((before, anchorLetter, after))
                wrapCheckWord(start, extraStart, anchorRow, anchorCol,
                              tilesLeft, possibleMoves, boardObj, across=across)
    return possibleMoves


def allMoves(rack, boardObj):
    acrossPlays = moveOneWay(rack, boardObj, True)
    flippedBoard = deepcopy(boardObj)
    flippedBoard.squares = flippedBoard.squares.transpose()
    downPlays = moveOneWay(rack, flippedBoard, False)
    return sorted(chain(acrossPlays, downPlays))

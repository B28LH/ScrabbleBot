"""Defines the Board() class and the essential Board operations

"""

import pickle
import numpy as np
from scrabbler.helpers import data
from scipy import ndimage


def posMove(row, col, across=True):  # Positive is up or left
    if across:
        if col > 0:
            return row, col - 1
    else:
        if row > 0:
            return row - 1, col
    return False


def negMove(row, col, size, across=True):  # Negative is down or right
    if across:
        if col < size - 1:
            return row, col + 1
    else:
        if row < size - 1:
            return row + 1, col
    return False


class Board:
    def __init__(self, title, design=data.official):
        r, c = design.shape
        self.squares = np.pad(design, ((0, r - 1), (0, c - 1)), 'reflect')
        self.size = len(self.squares)
        self.design = design
        self.title = title

    def __str__(self):
        Indices = list(map(str, range(self.size)))
        output = ''
        if self.size < 10:
            output += '    ' + '|'.join(Indices)
        else:
            output += '    ' + '|'.join([x[0] if int(x) > 9 else ' ' for x in Indices]) + '\n'
            output += '    ' + '|'.join([x[1] if int(x) > 9 else x for x in Indices]) + '\n'
        for i, x in enumerate(self.squares):
            if i < 10: i = str(i) + ' '
            output += str(i) + ' |' + ' '.join(x) + '\n'
        return output

    def __repr__(self):
        return str(self)

    def __setitem__(self, index, value):
        self.squares[index] = value

    def __getitem__(self, index):
        return self.squares[index]

    def AlphaArray(self):
        return np.isin(self.squares, data.alphabet).astype(int)

    def Layer(self, isAcross, coords, word):
        xC, yC = coords
        WordLen = len(word)
        if isAcross:
            assert yC + WordLen <= self.size, "Too large"
            self.squares[xC, yC:yC + WordLen] = list(word)
        else:  # down
            assert xC + WordLen <= self.size, "Too large"
            self.squares[xC:xC + WordLen, yC] = list(word)

    def Save(self, Name=None, Display=False):  # save objects or arrays?
        if Name is None:
            Name = self.title
        with open(data.abspath + f"ScrabbleGames/{Name}.pkl", 'wb') as f1:
            pickle.dump(self.squares, f1, pickle.HIGHEST_PROTOCOL)
        print(f"Game saved as {Name}\n")
        if Display:
            print(self)


def load(Name):  # Watch out for loading a deprecated Board object (or just an array)
    with open(data.abspath + f"ScrabbleGames/{Name}.pkl", 'rb') as f:
        LoadBoard = pickle.load(f)
    Loader = Board(Name)  # nb set the correct base design
    if type(LoadBoard) == np.ndarray:
        inData = LoadBoard
    else:
        inData = LoadBoard.squares
    Loader.squares = inData
    print(f"\nGame '{Name}' loaded \n\n{str(Loader)}")
    return Loader


def betterMoveTiles(boardObj, across=True):
    """ Finds the playable squares from a board

    :param boardObj: a Board() Object
    :param across: whether checking for horizontal (across) or vertical borders
    :return: an array of squares which satisfy border condition, and a list of those points
    """

    def leftright(arr):
        return np.any(arr * np.r_[0, 0, 0, 1, 0, 1, 0, 0, 0])

    def updown(arr):
        return np.any(arr * np.r_[0, 1, 0, 0, 0, 0, 0, 1, 0])

    Starters = np.where(boardObj.squares == '?', -1, 0)
    if np.any(Starters):
        return Starters, np.transpose(Starters.nonzero())
    if across:
        borderfunc = leftright
    else:
        borderfunc = updown
    tileLoc = boardObj.AlphaArray()
    surround = ndimage.generic_filter(tileLoc, borderfunc, size=(3, 3), mode='constant')
    output = (1 - tileLoc) * surround
    return output, np.transpose(output.nonzero())


def completeWord(boardObj, coord, across=True):  # Could make PosMove a generator?
    """ Finds longest line of letters from a spawn tile

    :param boardObj: a Board() Object
    :param coord: (row,col) of the spawn tile
    :param across: complete the word across (instead of down)
    :return: before, after, both strings, representing the contiguous tiles above/left and down/right
    """
    row, col = coord
    content = boardObj.AlphaArray()
    pospart = ''
    while True:
        tile = posMove(row, col, across)
        if tile and content[tile]:
            pospart += boardObj.squares[tile]
            row, col = tile
        else:
            break
    row, col = coord
    negpart = ''
    while True:
        tile = negMove(row, col, boardObj.size, across)
        if tile and content[tile]:
            negpart += boardObj.squares[tile]
            row, col = tile
        else:
            break
    return pospart[::-1], negpart


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

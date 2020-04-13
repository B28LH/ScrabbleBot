"""Defines the Board() and Move() class and the essential Board operations
"""

import pickle
import numpy as np
from copy import deepcopy
from scrabbler.major import data, algo


class Board:
    def __init__(self, design=data.official, title=None):
        r, c = design.shape
        self.design = design
        self.fullDesign = np.pad(design, ((0, r - 1), (0, c - 1)), 'reflect')
        self.squares = self.fullDesign
        self.size = len(self.squares)
        self.title = title

    def __str__(self):
        indices = list(map(str, range(self.size)))
        output = ''
        if self.size < 10:
            output += '    ' + '|'.join(indices)
        else:
            output += '    ' + '|'.join([x[0] if int(x) > 9 else ' ' for x in indices]) + '\n'
            output += '    ' + '|'.join([x[1] if int(x) > 9 else x for x in indices]) + '\n'
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

    def __delitem__(self, index):  # This resets the whole row to the design
        self.squares[index] = self.fullDesign[index]

    @property
    def alpha(self):
        return np.isin(self.squares, data.alphabet).astype(int)

    def layer(self, coords, word, across=True):
        """ Provides a visual representation of layer, to be approved by user """
        tempBoard = deepcopy(self)
        tempBoard.realLayer(coords, word, across=across)
        print(f"----New changes:-----\n {tempBoard}")
        answer = input("Apply changes? ")
        if answer != '' and answer.lower[0] == 'y':
            self.realLayer(coords, word, across=across)

    def realLayer(self, coords, word, across=True):
        row, col = coords
        wordLen = len(word)
        if across:
            assert col + wordLen <= self.size, "Too large"
            self.squares[row, col:col + wordLen] = list(word)
        else:  # down
            assert row + wordLen <= self.size, "Too large"
            self.squares[row:row + wordLen, col] = list(word)

    def save(self, saveName=None, Display=False):  # save objects or arrays?
        if saveName is None:
            assert self.title is not None, "saveName required"
            saveName = self.title
        with open(data.path + f"scrabbleGames/{saveName}.pkl", 'wb') as f1:
            pickle.dump(self.squares, f1, pickle.HIGHEST_PROTOCOL)
        print(f"Game saved as {saveName}\n")
        if Display:
            print(self)


def load(name, display=False):  # TODO: Fix loading to support objects?
    # TODO: Rewrite load function
    """ Loads a board from file into a BoardObj
    Watch out for loading a deprecated Board object (or just an array)

    :param name: The filename of the board you want to load
    :param display: whether the loaded board is printed
    :return: BoardObj: the loaded board
    """
    with open(data.path + f"scrabbleGames/{name}.pkl", 'rb') as f:  # THESE ONLY WORK WHEN EXECUTED FROM __main__.py
        LoadBoard = pickle.load(f)
    loader = Board(title=name)  # nb set the correct base design
    if type(LoadBoard) == np.ndarray:
        inData = LoadBoard
    else:
        inData = LoadBoard.squares
    loader.squares = inData
    if display:
        print(f"\nGame '{name}' loaded \n\n{loader}")
    return loader


def convert(word, behind):
    output = 0
    multiplier = 1
    if data.startTile:
        accept = ['!', '?']
    else:
        accept = ['!']
    for i, char in enumerate(word):
        if behind[i] == '*':
            output += 2 * data.tileValues[char]
        elif behind[i] == '^':
            output += 3 * data.tileValues[char]
        elif behind[i] in accept:
            multiplier *= 2
            output += data.tileValues[char]
        elif behind[i] == '#':
            multiplier *= 3
            output += data.tileValues[char]
        else:
            output += data.tileValues[char]
    return output * multiplier


def scorer(moveObj):
    """ scores a move
    :param moveObj: the move to be scored
    """
    moveObj.score = 0
    playedTiles = 0
    storedAlpha = moveObj.board.alpha
    initialBacking = moveObj.xray
    for i, char in enumerate(moveObj.word):
        if not storedAlpha[moveObj.row][moveObj.col + i]:
            playedTiles += 1
            before, after = algo.completeWord(moveObj.board, (moveObj.row, moveObj.col + i), across=False)
            if not (before is '' and after is ''):
                backing = [None] * (len(before) + len(after) + 1)
                backing[len(before)] = moveObj.xray[i]
                moveObj.score += convert(''.join((before, char, after)), backing)
        else:
            initialBacking[i] = None
    moveObj.score += convert(moveObj.word, initialBacking)
    if playedTiles == 7:
        moveObj.score += data.maxTile


class Move:
    # Every Move is an across move
    def __init__(self, word, coords, boardObj, score=None):
        self.word = word
        self.row, self.col = coords
        self.length = len(word)
        self.board = boardObj
        self.xray = boardObj.fullDesign[self.row, self.col:self.col + self.length]
        if score is None:
            scorer(self)
        else:
            self.score = score

    def __str__(self):
        if self.score is None:
            return f"{self.word} @ ({self.row},{self.col})"
        return f"{self.word} @ ({self.row},{self.col}) for {self.score} points"

    def __repr__(self):  # When is this called?
        return str(self)

    def __lt__(self, other):
        return self.score < other.score

    def __eq__(self, other):
        # Do I need to compare scores?
        return self.score == other.score and self.row == other.row and self.col == other.col

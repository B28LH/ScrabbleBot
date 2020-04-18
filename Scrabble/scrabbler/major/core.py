"""Defines the Board() and Move() class and the essential Board operations
"""

import pickle
import numpy as np
from copy import deepcopy
from scrabbler.major import data, algo


class Board:
    def __init__(self, title=None):
        r, c = data.design.shape
        self.design = data.design
        self.fullDesign = np.pad(data.design, ((0, r - 1), (0, c - 1)), 'reflect')
        self.squares = self.fullDesign
        self.size = len(self.squares)
        self.title = title
        self.cachedAlpha = self.alpha

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

    def __getitem__(self, index):
        self.cachedAlpha = self.alpha
        return self.squares[index]

    def __delitem__(self, index):  # This resets the whole row to the design
        self[index] = self.fullDesign[index]
        self.cachedAlpha = self.alpha

    @property
    def alpha(self):
        return np.isin(self.squares, data.alphabet).astype(int)

    def layer(self, coords, word, across=True):
        """ Provides a visual representation of layer, to be approved by user """
        tempBoard = deepcopy(self)
        tempBoard.realLayer(coords, word, across=across)
        print(f"----New changes:------\n {tempBoard}")
        answer = input("Apply changes? ")
        if answer != '' and answer.lower()[0] == 'y':
            self.realLayer(coords, word, across=across, display=False)

    def realLayer(self, coords, word, across=True, display=False):
        """ No return layer of move"""
        row, col = coords
        wordLen = len(word)
        if across:
            assert col + wordLen <= self.size, "Too large"
            self.squares[row, col:col + wordLen] = list(word)
        else:  # down
            assert row + wordLen <= self.size, "Too large"
            self.squares[row:row + wordLen, col] = list(word)
        if display:
            print(self)
        self.cachedAlpha = self.alpha

    def layerMoveObj(self, moveObj, display=True):
        self.realLayer(moveObj.coords, moveObj.word, across=moveObj.across, display=display)

    def save(self, saveName=None, Display=False):  # save objects or arrays?
        if saveName is None:
            assert self.title is not None, "saveName required"
            saveName = self.title
        with open(data.path + f"scrabbleGames/{saveName}.pkl", 'wb') as f1:
            pickle.dump(self.squares, f1, pickle.HIGHEST_PROTOCOL)
        print(f"Game saved as {saveName}\n")
        if Display:
            print(self)


def load(name, display=False):
    # TODO: Rewrite load function (support objects?)
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
    loader.cachedAlpha = loader.alpha
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
        char = char.lower()  # TODO: Fix this bug
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
    score = 0
    playedTiles = 0
    initialBacking = np.array(moveObj.xray)
    for i, char in enumerate(moveObj.word):
        if not moveObj.board.cachedAlpha[moveObj.fakeRow][moveObj.fakeCol + i]:
            playedTiles += 1
            before, after = algo.completeWord(moveObj.board, (moveObj.fakeRow, moveObj.fakeCol + i), across=False)
            if not (before == '' and after == ''):
                backing = [None] * (len(before) + len(after) + 1)
                backing[len(before)] = moveObj.xray[i]
                score += convert(''.join((before, char, after)), backing)
        else:
            initialBacking[i] = None
    score += convert(moveObj.word, initialBacking)
    if playedTiles == data.maxTile:
        score += data.allTileBonus
    return score


class Move:
    def __init__(self, word, coords, boardObj, across, score=None):
        self.word = word
        self.row, self.col = self.coords = coords
        self.length = len(word)
        self.across = across
        self.board = boardObj
        if across:
            self.xray = boardObj.fullDesign[self.row, self.col:self.col + self.length]
            self.fakeRow, self.fakeCol = coords
        else:
            self.xray = boardObj.fullDesign[self.row:self.row + self.length, self.col]
            self.fakeCol, self.fakeRow = coords
        if score is None:
            self.score = scorer(self)
        else:
            self.score = score

    def __str__(self):
        if self.across:
            return f"across: {self.word} @ {self.coords} for {self.score} points"
        else:
            return f"down: {self.word} @ {self.coords} for {self.score} points"

    def __repr__(self):  # When is this called?
        if self.across:
            return f"→ {self.word} ({self.row},{self.col}) {self.score}p"
        else:
            return f"↓ {self.word} ({self.row},{self.col}) {self.score}p"

    def __lt__(self, other):
        return self.score < other.score

    def __eq__(self, other):
        # Do I need to compare scores?
        return self.score == other.score and self.row == other.row and self.col == other.col

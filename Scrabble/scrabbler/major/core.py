"""Defines the Board() class and the essential Board operations
"""

import pickle
import numpy as np
from scrabbler.major import data


class Board:
    def __init__(self, title, design=data.official):
        r, c = design.shape
        self.design = design
        self.fullDesign = np.pad(design, ((0, r - 1), (0, c - 1)), 'reflect')
        self.squares = self.fullDesign
        self.size = len(self.squares)
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

    def AlphaArray(self):  # This really should be an attribute, not a method
        return np.isin(self.squares, data.alphabet).astype(int)

    def layer(self, coords, word, across=True):
        row, col = coords
        WordLen = len(word)
        if across:
            assert col + WordLen <= self.size, "Too large"
            self.squares[row, col:col + WordLen] = list(word)
        else:  # down
            assert row + WordLen <= self.size, "Too large"
            self.squares[row:row + WordLen, col] = list(word)

    # TODO: create a 'cancel' function which deletes last word

    def save(self, Name=None, Display=False):  # save objects or arrays?
        if Name is None:
            Name = self.title
        with open(f"ScrabbleGames/{Name}.pkl", 'wb') as f1:  # THESE ONLY WORK WHEN EXECUTED FROM __main__.py
            pickle.dump(self.squares, f1, pickle.HIGHEST_PROTOCOL)
        print(f"Game saved as {Name}\n")
        if Display:
            print(self)


class Move:
    # Every Move is an across move
    def __init__(self, word, startCoords, boardObj, score=None):
        self.word = word
        self.row, self.col = startCoords
        self.length = len(word)
        self.score = self.score()
        self.xray = boardObj.fullDesign[self.row, self.col:self.col + self.length]

    def score(self):
        pass  # TODO: implement scoring
        return 1

    def __str__(self):
        if self.score is None:
            return f"{self.word} @ ({self.row},{self.col})"
        return f"{self.word} @ ({self.row},{self.col}) for {self.score} points"

    def __repr__(self):  # When is this called?
        return str(self)

    def __lt__(self, other):
        return self.score < other.score


def load(name, display=False):
    """ Loads a board from file into a BoardObj
    Watch out for loading a deprecated Board object (or just an array)
    
    :param Name: The filename of the board you want to load
    :return: BoardObj: the loaded board
    """
    with open(f"ScrabbleGames/{name}.pkl", 'rb') as f:  # THESE ONLY WORK WHEN EXECUTED FROM __main__.py
        LoadBoard = pickle.load(f)
    Loader = Board(name)  # nb set the correct base design
    if type(LoadBoard) == np.ndarray:
        inData = LoadBoard
    else:
        inData = LoadBoard.squares
    Loader.squares = inData
    if display:
        print(f"\nGame '{name}' loaded \n\n{Loader}")
    return Loader



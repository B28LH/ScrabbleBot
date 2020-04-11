"""Defines the Board() class and the essential Board operations
"""

import pickle
import numpy as np
from scrabbler.helpers import data


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

    def AlphaArray(self):  # This really should be an attribute, not a method
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
        with open(f"ScrabbleGames/{Name}.pkl", 'wb') as f1:  # THESE ONLY WORK WHEN EXECUTED FROM __main__.py
            pickle.dump(self.squares, f1, pickle.HIGHEST_PROTOCOL)
        print(f"Game saved as {Name}\n")
        if Display:
            print(self)


def load(Name):  # Watch out for loading a deprecated Board object (or just an array)
    with open(f"ScrabbleGames/{Name}.pkl", 'rb') as f:  # THESE ONLY WORK WHEN EXECUTED FROM __main__.py
        LoadBoard = pickle.load(f)
    Loader = Board(Name)  # nb set the correct base design
    if type(LoadBoard) == np.ndarray:
        inData = LoadBoard
    else:
        inData = LoadBoard.squares
    Loader.squares = inData
    print(f"\nGame '{Name}' loaded \n\n{Loader}")
    return Loader



import numpy as np
from helpers import data
import pickle


class Board:
    def __init__(self, title, design=data.official):
        r, c = design.shape
        self.data = np.pad(design, ((0, r - 1), (0, c - 1)), 'reflect')
        self.size = len(self.data)
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
        for i, x in enumerate(self.data):
            if i < 10: i = str(i) + ' '
            output += str(i) + ' |' + ' '.join(x) + '\n'
        return output

    def __repr__(self):
        return str(self)

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getitem__(self, index):
        return self.data[index]

    def AlphaArray(self):
        return np.isin(self.data, list(data.alphabet)).astype(int)

    def Layer(self, isAcross, coords, word):
        xC, yC = coords
        WordLen = len(word)
        if isAcross:
            assert yC + WordLen <= self.size, "Too large"
            self.data[xC, yC:yC + WordLen] = list(word)
        else:  # down
            assert xC + WordLen <= self.size, "Too large"
            self.data[xC:xC + WordLen, yC] = list(word)

    def Save(self, Name=None, Display=False):  # save objects or arrays?
        if Name is None:
            Name = self.title
        with open(f"../ScrabbleGames/{Name}.pkl", 'wb') as f1:
            pickle.dump(self.data, f1, pickle.HIGHEST_PROTOCOL)
        print(f"Game saved as {Name}\n")
        if Display:
            print(self)


def Load(Name):  ## Watch out for loading a depricated Board object (or just an array)
    with open('../ScrabbleGames/%s.pkl' % Name, 'rb') as f:
        LoadBoard = pickle.load(f)
    Loader = Board(Name)  # nb set the correct base design
    if type(LoadBoard) == np.ndarray:
        inData = LoadBoard
    else:
        inData = LoadBoard.data
    Loader.data = inData
    print(f"\nGame '{Name}' loaded \n\n{str(Loader)}")
    return Loader

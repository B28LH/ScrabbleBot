import numpy as np
import string

# Essential variables

addOn = [(1, 0), (0, 1), (-1, 0), (0, -1)]
alphabet = list(string.ascii_letters)
loweralpha = list(string.ascii_lowercase)
maxTile = 7
path = '/Users/Ben/Documents/PythonScripts/Best Scripts/Scrabble/'

# Bags
sTileValues = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
               "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
               "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
               "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
               "x": 8, r"z": 10}

wTileValues = {"a": 1, "c": 4, "b": 4, "e": 1, "d": 2, "g": 3,
               "f": 4, "i": 1, "h": 3, "k": 5, "j": 10, "m": 4,
               "l": 2, "o": 1, "n": 2, "q": 10, "p": 4, "s": 1,
               "r": 1, "u": 2, "t": 1, "w": 4, "v": 5, "y": 3,
               "x": 8, "z": 10}

bagamts = {"a": 9, "c": 2, "b": 2, "e": 12, "d": 4, "g": 3,
           "f": 2, "i": 9, "h": 2, "k": 1, "j": 1, "m": 2,
           "l": 4, "o": 8, "n": 6, "q": 1, "p": 2, "s": 4,
           "r": 6, "u": 4, "t": 6, "w": 2, "v": 2, "y": 2,
           "x": 1, "z": 1}


# Boards

# Notation: *x is double ^x is triple, multiplier can be keyword
# Board: ! is double word, # is triple, ? is start

officialQuad = ['#--*---#', '-!---^--', '--!---*-',
            '*--!---*', '----!---', '-^---^--',
            '--*---*-', '#--*---?']
friendsSmallQuad = ['^-#---', '-*---*', '#-^-*-', '---^--', '--*---', '-*---?']
friendsBigQuad = ['---#--^-', '--*--!--', '-*--*---', '#--^---!', '--*---*-',
              '-!---^--', '^---*---', '---!---?']

official = np.array([list(x) for x in officialQuad])
friendsSmall = np.array([list(x) for x in friendsSmallQuad])
friendsBig = np.array([list(x) for x in friendsBigQuad])

# Essential Globals

dictfile = 'collins.txt'
wordset = None
meaningdict = None
allTileBonus = 50
startTile = True
tileValues = sTileValues
design = friendsBig

gameBoard = None

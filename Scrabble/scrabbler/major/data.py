import numpy as np
import string

# Essential variables

addOn = [(1, 0), (0, 1), (-1, 0), (0, -1)]
alphabet = list(string.ascii_letters)
loweralpha = list(string.ascii_lowercase)
maxTile = 7
path = '/Users/Ben/Documents/PythonScripts/Best Scripts/Scrabble/scrabbler/'  # change this when moving directories

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

officialQuad = ['#--*---#',
                '-!---^--',
                '--!---*-',
                '*--!---*',
                '----!---',
                '-^---^--',
                '--*---*-',
                '#--*---?']
friendsSmallQuad = ['^-#---',
                    '-*---*',
                    '#-^-*-',
                    '---^--',
                    '--*---',
                    '-*---?']
friendsBigQuad = ['---#--^-',
                  '--*--!--',
                  '-*--*---',
                  '#--^---!',
                  '--*---*-',
                  '-!---^--',
                  '^---*---',
                  '---!---?']

official = np.array([list(x) for x in officialQuad])
friendsSmall = np.array([list(x) for x in friendsSmallQuad])
friendsBig = np.array([list(x) for x in friendsBigQuad])

# Essential Globals

dictfile = None
wordset = None
meaningDict = None
completor = None

allTileBonus = None
startTile = None
tileValues = None
design = None

gameBoard = None
crossed = None

testcase = [('ea', (9, 4)), ('ae', (9, 5)), ('re', (10, 5)), ('ee', (10, 8)), ('en', (11, 8)), ('ne', (11, 9)),
            ('te', (12, 9)), ('et', (12, 8)), ('es', (6, 4)), ('ee', (8, 4)), ('oe', (8, 9)), ('ma', (9, 4)),
            ('am', (9, 5)), ('em', (9, 8)), ('me', (9, 9)), ('er', (10, 4)), ('me', (10, 8)), ('ee', (10, 9)),
            ('mae', (9, 4)), ('eme', (10, 7)), ('mee', (10, 7)), ('em', (6, 10)), ('ee', (8, 5)), ('mm', (9, 8)),
            ('mm', (9, 9)), ('met', (12, 7)), ('mes', (6, 3)), ('mee', (8, 3)), ('mem', (9, 7)), ('mem', (9, 9)),
            ('me', (6, 10)), ('me', (8, 4)), ('om', (8, 9)), ('em', (10, 9)), ('men', (11, 7)), ('ems', (6, 3)),
            ('eme', (8, 3)), ('erm', (10, 4)), ('mee', (10, 8)), ('eme', (10, 9)), ('mee', (8, 4)), ('em', (8, 5)),
            ('mo', (8, 8)), ('em', (6, 7)), ('moe', (8, 8))]

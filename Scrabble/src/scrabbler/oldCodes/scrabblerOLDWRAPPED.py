from itertools import permutations as pm
from collections import Counter

from bisect import bisect_left
import numpy as np
import random
import re
import string
import pickle

# TODO:
# DONT DO DEFAULT VARIABLES
# Implement meaning for every word p layed
# Recover changes from last time
# Word exeption override

path = '/Users/Ben/BLH Documents/Coding/PythonScripts/Best Scripts/Scrabble/src/scrabbler/'
AddOn = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # For surrounding tiles
WWF = False  # Playing Words With Friends or traditional Scrabble
Small = False  # Small or large board
MaxTile = 7
GameName = 'test4'

STileValues = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
               "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
               "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
               "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
               "x": 8, "z": 10}

WTileValues = {"a": 1, "c": 4, "b": 4, "e": 1, "d": 2, "g": 3,
               "f": 4, "i": 1, "h": 3, "k": 5, "j": 10, "m": 4,
               "l": 2, "o": 1, "n": 2, "q": 10, "p": 4, "s": 1,
               "r": 1, "u": 2, "t": 1, "w": 4, "v": 5, "y": 3,
               "x": 8, "z": 10}

bagamts = {"a": 9, "c": 2, "b": 2, "e": 12, "d": 4, "g": 3,
           "f": 2, "i": 9, "h": 2, "k": 1, "j": 1, "m": 2,
           "l": 4, "o": 8, "n": 6, "q": 1, "p": 2, "s": 4,
           "r": 6, "u": 4, "t": 6, "w": 2, "v": 2, "y": 2,
           "x": 1, "z": 1}

if WWF:
    file = 'wwf.txt'
    allTileBonus = 35
    startTile = False
    TileValues = WTileValues
else:
    file = 'collins.txt'
    allTileBonus = 50
    startTile = True
    TileValues = STileValues

for char in string.ascii_uppercase:
    TileValues[char] = 0


def Refresh():
    global TileBag
    TileBag = list(Counter(bagamts).elements())
    random.shuffle(TileBag)


def TakeTiles(numb):  # Could definitely clean this up
    random.shuffle(TileBag)
    numb = min(numb, len(TileBag))
    out = []
    for i in range(numb):
        out.append(TileBag.pop())
    return out


# Notation: *x is double ^x is triple, multiplier can be keyword, capital is blank
# Board: ! is double word, # is triple, ? is start
FirstQuad = ['#--*---#', '-!---^--', '--!---*-',
             '*--!---*', '----!---', '-^---^--',
             '--*---*-', '#--*---?']

FriendsSmall = ['^-#---', '-*---*', '#-^-*-', '---^--', '--*---', '-*---?']
FriendsBig = ['---#--^-', '--*--!--', '-*--*---', '#--^---!', '--*---*-',
              '-!---^--', '^---*---', '---!---?']

if WWF:
    if Small:
        chosen = FriendsSmall
    else:
        chosen = FriendsBig
else:
    chosen = FirstQuad
b2 = [x + x[-2::-1] for x in chosen]
for item in b2[-2::-1]:
    b2.append(item)

width = len(b2[0])  # VERY important variable

StartBoard = np.array([list(x) for x in b2])
GameBoard = np.copy(StartBoard)

with open(path + 'oldCodes/' + file, 'r') as file:
    words = file.read().split()
    words = set(words)


def isWord(word):
    return word in words


with open(path + 'oldCodes/' + 'collinsdict.pkl', 'rb') as f:
    collinsdict = pickle.load(f)


def DisplayBoard(grid=GameBoard):
    h = range(len(grid))
    if len(grid) < 10:
        print('    ' + '|'.join(map(str, h)))
    else:
        print('    ' + '|'.join([x[0] if int(x) > 9 else ' ' for x in map(str, h)]))
        print('    ' + '|'.join([x[1] if int(x) > 9 else x for x in map(str, h)]))
    for i, x in enumerate(grid):
        if i < 10: i = str(i) + ' '
        print(i, '|' + ' '.join(x))


DisplayBoard(StartBoard)


def ValidNear(xCord, yCord):
    t = [(xCord + x[0], yCord + x[1]) for x in AddOn]
    return [x for x in t if 0 <= x[0] < width and 0 <= x[1] < width]


def ValidVert(xCord, yCord):
    return [x for x in ((xCord + 1, yCord), (xCord - 1, yCord)) if 0 <= x[0] < width and 0 <= x[1] < width]


def ValidHorz(xCord, yCord):
    return [x for x in ((xCord, yCord + 1), (xCord, yCord - 1)) if 0 <= x[0] < width and 0 <= x[1] < width]


# Puts down a word horizontally from xC, yC
def LayAcross(xC, yC, word, GameBoard):  # fix this
    n = len(word)
    if yC + n > width:
        return False
    bit = GameBoard[xC]
    for i in range(n):
        bit[yC + i] = word[i]
    GameBoard[xC] = bit
    return GameBoard


def LayDown(xC, yC, word, GameBoard):
    n = len(word)
    if xC + n > width:
        return False
    GameBoard[xC:xC + n, yC] = list(word)
    return GameBoard


def Layer(Orient, xC, yC, word, GameBoard):
    if Orient == 1:
        return LayDown(xC, yC, word, GameBoard)
    else:
        return LayAcross(xC, yC, word, GameBoard)


# Finds the possible start tiles, returns a board and a list
# 3 means both, 2 is vertical, 1 is horizontal, 0 is none, -1 is start
def MoveTiles(GameBoard):
    StartingSquares = np.zeros((width, width))
    StartTilesList = []
    wid = range(width)
    for xCord in wid:
        for yCord in wid:
            if GameBoard[xCord][yCord] == '?':
                StartingSquares[xCord][yCord] = -1
                return (StartingSquares, [(xCord, yCord)])
            elif not GameBoard[xCord][yCord].isalpha():
                Vertical = any([GameBoard[x1][y1].isalpha() for x1, y1 in ValidVert(xCord, yCord)])
                Horizontal = any([GameBoard[x1][y1].isalpha() for x1, y1 in ValidHorz(xCord, yCord)])
                if Vertical or Horizontal:
                    StartTilesList.append((xCord, yCord))
                if Vertical and Horizontal:
                    StartingSquares[xCord][yCord] = 3
                elif Horizontal:
                    StartingSquares[xCord][yCord] = 2
                elif Vertical:
                    StartingSquares[xCord][yCord] = 1
    return (StartingSquares, StartTilesList)


# Easy Fix
def GetWork(row, col, GameBoard, Across):  # Returns Workspace and start (entire row/columm)
    if Across:
        Workspace = list(GameBoard[row])
        Start = col
    else:
        Workspace = list(GameBoard[:, col])
        Start = row
    return (Workspace, Start)


def FindAll(row, col, GameBoard, Across):  # Across = False means vert
    Workspace, Start = GetWork(row, col, GameBoard, Across)
    initial = Workspace[Start]
    if initial.isalpha():
        output = [initial]
    else:
        output = ['.']
    Second = Start + 1
    Start -= 1
    while Start >= 0 and (Workspace[Start].isalpha() or Workspace[Start] in ['.', '?']):
        output = [Workspace[Start]] + output
        Start -= 1
    while Second < width and (Workspace[Second].isalpha() or Workspace[Second] in ['.', '?']):
        output.append(Workspace[Second])
        Second += 1
    return (''.join(output), Start + 1)


def NumGen(Length, Pos):  # Provides all possible subsets of from a position
    AllPos = []
    for i in range(1, Length + 2):
        for x in range(Length - i + 1):
            AllPos.append((x, x + i))
    return [x for x in AllPos if x[0] <= Pos < x[1]]


def TestStart(item, GameBoard):
    if not item[0][0].isalpha():
        xCord, yCord = item[1][1][0], item[1][1][1]
        if item[1][0] == 1:
            xCord -= 1
        else:
            yCord -= 1
        if xCord >= 0 and yCord >= 0 and GameBoard[xCord][yCord].isalpha():
            return False
    return True


def TestEnd(item, GameBoard):
    if not item[0][-1].isalpha():
        xCord, yCord = item[1][2][0], item[1][2][1]
        if item[1][0] == 1:
            xCord += 1
        else:
            yCord += 1
        if xCord < width and yCord < width and GameBoard[xCord][yCord].isalpha():
            return False
    return True


# All possible places to play from a given r,c and length
def BothWays(row, col, GameBoard, i, MoveBoard, length):  # 1 = Vert, 2 = Horz
    Work, Pos = GetWork(row, col, GameBoard, i == 2)
    if i == 1:  # Vertical
        # Returns all possible play tiles (i.e -*p-), their orientation and start and end points
        Splits = [(Work[a:b], (i, (a, col), (b, col))) for a, b in NumGen(len(Work), Pos)]
    else:  # Horizontal
        Splits = [(Work[a:b], (i, (row, a), (row, b))) for a, b in NumGen(len(Work), Pos)]
    # Ensures all splits contains a letter
    Splits = [x for x in Splits if [y.isalpha() for y in x[0]].count(0) <= length and len(x[0]) > 1]
    # ensures that the start and end aren't next to a filled in tile
    Splits = [x for x in Splits if TestStart(x, GameBoard) and TestEnd(x, GameBoard)]
    Result = MoveBoard[row][col]
    Truth = FindAll(row, col, GameBoard, i == 2)[0]
    Real = []
    if Result == 3 or Result == i:
        for item in Splits:
            if re.search(Truth, ''.join(item[0])):
                Real.append(item)
        return Real
    else:
        return Splits


def AllGood(Direction, Start, Word, GameBoard):
    Tester = np.copy(GameBoard)
    Layer(Direction, Start[0], Start[1], Word, Tester)
    if not isWord(FindAll(Start[0], Start[1], Tester, Direction == 2)[0].lower()):
        return False
    attemptBoard = np.copy(GameBoard)
    if Direction == 1:
        OpDir = 2
        AllTiles = [(Start[0] + i, Start[1]) for i in range(len(Word))]
        LayDown(Start[0], Start[1], Word, attemptBoard)
    else:
        OpDir = 1
        AllTiles = [(Start[0], Start[1] + i) for i in range(len(Word))]
        LayAcross(Start[0], Start[1], Word, attemptBoard)
    for r, c in AllTiles:
        Others = FindAll(r, c, attemptBoard, OpDir == 2)[0]
        if len(Others) > 1 and not isWord(Others.lower()):
            return False
    return True


def Convert(Word, Behind):
    Output = 0
    Multiplier = 1
    if startTile:
        accept = ['!', '?']
    else:
        accept = ['!']
    for i, char in enumerate(Word):
        if Behind[i] == '*':
            Output += 2 * TileValues[char]
        elif Behind[i] == '^':
            Output += 3 * TileValues[char]
        elif Behind[i] in accept:
            Multiplier *= 2
            Output += TileValues[char]
        elif Behind[i] == '#':
            Multiplier *= 3
            Output += TileValues[char]
        else:
            Output += TileValues[char]
    return Output * Multiplier


def Score(Direction, Start, Word, GameBoard, AllUsed, MoveBoard):
    total = 0
    newBoard = np.copy(GameBoard)
    if Direction == 1:
        LayDown(Start[0], Start[1], Word, newBoard)
        under = [GameBoard[Start[0] + i][Start[1]] for i in range(len(Word))]
    else:
        LayAcross(Start[0], Start[1], Word, newBoard)
        under = GameBoard[Start[0]][Start[1]:Start[1] + len(Word)]
    total += Convert(Word, under)
    for i in range(len(Word)):
        if Direction == 1:
            r, c = Start[0] + i, Start[1]
            OpDir = True
        else:
            r, c = Start[0], Start[1] + i
            OpDir = False
        if not GameBoard[r][c].isalpha() and MoveBoard[r][c] != 0:
            alt = FindAll(r, c, newBoard, OpDir)
            if len(alt[0]) > 1:
                if Direction == 2:
                    under = [GameBoard[alt[1] + i][c] for i in range(len(alt[0]))]
                else:
                    under = GameBoard[r][alt[1]:alt[1] + len(alt[0])]
                total += Convert(alt[0], under)
    if AllUsed:
        total += allTileBonus
    return total


def BestMove(Tiles, GameBoard):
    if '&' in Tiles:
        alternate = list(Tiles)
        alternate.remove('&')
        master = []
        for item in string.ascii_uppercase:
            newTiles = alternate + [item]
            a = BestMove(newTiles, GameBoard)[-7:]
            if a:
                master.extend(a)
        if len(master) > 0:
            return sorted(master, key=lambda x: x[-1])
        return False
    Moves = []
    MoveBoard, GoodTiles = MoveTiles(GameBoard)
    SolvedCases = {}
    for row, col in GoodTiles:
        Section = []
        for i in (1, 2):
            for item in BothWays(row, col, GameBoard, i, MoveBoard, len(Tiles)):
                Section.append(item)
        for item in Section:
            valids = []
            fills = [x.isalpha() for x in item[0]].count(0)  # number of blanks in selection
            if fills not in SolvedCases:  # generates new permuations
                SolvedCases[fills] = list(set([''.join(x) for x in list(set(pm(Tiles, fills)))]))
            for part in SolvedCases[fills]:  # building out the new word
                a, attempt = 0, ''
                for char in item[0]:
                    if char.isalpha():
                        attempt += char
                    else:
                        attempt += part[a]
                        a += 1
                if isWord(attempt.lower()):
                    if a == MaxTile:
                        valids.append((attempt, True))
                    else:
                        valids.append((attempt, False))
            for piece in valids:
                if AllGood(item[1][0], item[1][1], piece[0], GameBoard):
                    Start = item[1][1]
                    Direction = item[1][0]
                    Points = Score(Direction, Start, piece[0], GameBoard, piece[1], MoveBoard)
                    Assembly = (Direction, Start, piece[0], Points)
                    if Assembly not in Moves:
                        Moves.append(Assembly)
    result = sorted(Moves, key=lambda x: x[-1])
    if len(result) > 0:
        return result
    return False


def CompvsComp(Moves):
    Refresh()
    GameBoard = np.copy(StartBoard)
    Comp1 = 0
    Comp2 = 0
    while Moves > 0 and len(TileBag) > 0:
        let = TakeTiles(7)
        BMP = BestMove(let, GameBoard)
        if BMP:
            BMP = BMP[-1]
            Layer(BMP[0], BMP[1][0], BMP[1][1], BMP[2], GameBoard)
            print("\n\nWith letters %s,\nI play %s for %i points\n" % (' '.join(let), BMP[2], BMP[3]))
            if Moves % 2 == 0:
                Comp1 += BMP[3]
                print("Comp1's move")
            else:
                print("Comp2's move")
                Comp2 += BMP[3]
            print("Scores:\n\tComp1: %i\n\tComp2: %i" % (Comp1, Comp2))
            DisplayBoard(GameBoard)
        else:
            print("With letter(s) %s,\nI cannot play a move" % (' '.join(let)))
        Moves -= 1


def Meaning(word):
    print('{}: {}'.format(word, collinsdict[word.lower()]))


# def Meaning2(word):  # deprecated
#     Meaning = EngDict.meaning(word.lower())
#     if Meaning == None:
#         print("'%s' is not a word in the dictionary" % word)
#         return
#     print("'%s' means:" % word)
#     for key in Meaning:
#         print(key + '')
#         for num, definition in enumerate(Meaning[key]):
#             print('\t%i %s' % (num + 1, definition))


def play(MyLetters, GameBoard=GameBoard, Difficulty=3):
    TheMoves = BestMove(MyLetters, GameBoard)
    if TheMoves:
        Scores = np.array([part[3] for part in TheMoves])
        TargetScore = round(Scores.mean() + Difficulty * Scores.std())
        print(list((reversed(TheMoves[-20:]))))
        for index, item in enumerate(TheMoves):
            if item[3] >= TargetScore:
                MyMove = TheMoves[index]
                break
        print("I play %s for %i points, at (%i, %i)\n" % (MyMove[2], MyMove[3], MyMove[1][0], MyMove[1][1]))
        Layer(MyMove[0], MyMove[1][0], MyMove[1][1], MyMove[2], GameBoard)
        DisplayBoard(GameBoard)
        Meaning(MyMove[2])
    else:
        print("With letters %s,\nI cannot play a move" % (' '.join(MyLetters)))


def InputFormat(string, GameBoard):
    trans = string.split()
    if trans[0] == 'd':
        Dir = 1
    else:
        Dir = 2
    row, col = int(trans[1]), int(trans[2])
    word = trans[3]
    MB = MoveTiles(GameBoard)[0]
    return (Dir, (row, col), word, MB)


def SaveGame(GameBoard, Name=GameName):
    DisplayBoard(GameBoard)
    with open(f'{path}scrabbleGames/{Name}', 'wb') as f1:
        pickle.dump(GameBoard, f1, pickle.HIGHEST_PROTOCOL)
    print("Game saved as", Name)


def LoadGame(Name=GameName):
    with open(f'{path}scrabbleGames/{Name}', 'rb') as f:
        GameBoard = pickle.load(f)
    print("Game '%s' loaded" % Name)
    DisplayBoard(GameBoard)
    return GameBoard


def MoveEval(Word, Tiles, GameBoard, CompMoves):
    testGame = np.copy(GameBoard)
    Dir, Start, word, MB = InputFormat(Word, testGame)
    if not CompMoves:
        CompMoves = BestMove(Tiles, GameBoard)
    MyMove = (Dir, Start, word, Score(Dir, Start, word, GameBoard, False, MB))
    for i, x in enumerate(CompMoves):
        if x == MyMove:
            maxScore = CompMoves[-1][-1]
            total = len(CompMoves)
            print("Playing %s for %i points:" % (MyMove[2], MyMove[-1]))
            print("\t{}% of possible points".format(round(MyMove[-1] * 100 / maxScore, 2)))
            print("\tWord %i out of %i" % (total - i, total))
            break
    else:
        print("Not a valid word")
    return CompMoves


def CheckInput(initial, GameBoard=GameBoard, Play=True):
    Dir, Start, word, MB = InputFormat(initial, GameBoard)
    if Dir == 1:
        CovSquare = [(Start[0] + i, Start[1]) for i in range(len(word))]
    else:
        CovSquare = [(Start[0], Start[1] + i) for i in range(len(word))]
    for x, (r, c) in enumerate(CovSquare):
        if GameBoard[r][c].isalpha() and GameBoard[r][c] != word[x]:
            print("Not a valid move")
            return False
    if AllGood(Dir, Start, word, GameBoard):
        print("\n%s scores %i points\n" % (word, Score(Dir, Start, word, GameBoard, False, MB)))
        if Play:
            Layer(Dir, Start[0], Start[1], word, GameBoard)
            DisplayBoard(GameBoard)
    else:
        print("Not a valid move")

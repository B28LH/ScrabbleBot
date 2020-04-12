from itertools import permutations as pm
from collections import Counter
# from PyDictionary import PyDictionary
from bisect import bisect_left
import numpy as np
import random
import re
import string
import pickle

# EngDict = PyDictionary()

AddOn = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # For surrounding tiles
WWF = True  # Playing Words With Friends or traditional Scrabble
Small = False  # Small or large board
MaxTile = 7
GameName = 'test4'


def binsrch2(lst, item):
    return (item <= lst[-1]) and (lst[bisect_left(lst, item)] == item)


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
    file = 'scra.txt'
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


with open(file, 'r') as file:
    words = file.read().split()

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


def DisplayBoard(grid):
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
        Workspace = [GameBoard[i][col] for i in range(width)]
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
    if not binsrch2(words, FindAll(Start[0], Start[1], Tester, Direction == 2)[0].lower()):
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
        if len(Others) > 1 and not binsrch2(words, Others.lower()):
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
                if binsrch2(words, attempt.lower()):
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


def DisplayMeaning(word):
    Meaning = EngDict.meaning(word.lower())
    if Meaning == None:
        print("'%s' is not a word in the dictionary" % word)
        return
    print("'%s' means:" % word)
    for key in Meaning:
        print(key + '')
        for num, definition in enumerate(Meaning[key]):
            print('\t%i %s' % (num + 1, definition))


def play(MyLetters, GameBoard):
    TheMoves = BestMove(MyLetters, GameBoard)
    if TheMoves:
        MyMove = TheMoves[-1]
        print("I play %s for %i points\n" % (MyMove[2], MyMove[3]))
        Layer(MyMove[0], MyMove[1][0], MyMove[1][1], MyMove[2], GameBoard)
        DisplayBoard(GameBoard)
        print(list(reversed(TheMoves[-10:])))  # Do I need to print all the other options?
        # DisplayMeaning(MyMove[2])
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


def isWord(word):
    print(binsrch2(words, word.lower()))


def SaveGame(GameBoard, Name=GameName):
    with open('../scrabbleGames/%s.pkl' % Name, 'wb') as f1:
        pickle.dump(GameBoard, f1, pickle.HIGHEST_PROTOCOL)
    print("Game saved as", Name)


def LoadGame(GameBoard, Name=GameName):
    with open('../scrabbleGames/%s.pkl' % Name, 'rb') as f:
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


def CheckInput(initial, GameBoard, Play):
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


import cProfile

GameBoard = LoadGame(GameBoard, 'Oscar2')
cProfile.run('play("asdflet",GameBoard)', sort=1)

###---------Area to play in------------####


#Wipe GameBoard
GameBoard = np.copy(StartBoard)

#Show the game
DisplayBoard(GameBoard)

#Save the game, name defaults to GameName
SaveGame(GameBoard,'Oscar1')

#Load a previous game. Second variable is the name of the file (optional)
GameBoard = LoadGame(GameBoard, 'Oscar2')

#Check if a word is valid
isWord('oiler')

# Lookup word in dictionary
DisplayMeaning("neuritis")

# Check to see if a given play is valid: CheckInput(initial,GameBoard,Play)
# initial is a move string ('d 5 6 rosey' (row,column))
# GameBoard is the board
# Play is True when you want the move to be entered, False if just check
Choice = 'a 14 1 kerns'
CheckInput(Choice,GameBoard,True)
# Computer's letters (a blank is denoted by &)
BotLetters = list('kernsgn')

# Ask the Computer to play a move
#play(BotLetters,GameBoard)


# Ranking a human move
HumanLetters = 'yifighi'
HumanPlay = 'a 11 7 jet'

# Creates a move evaluation (for first time)
Evaluation = MoveEval(HumanPlay,list(HumanLetters),GameBoard,False)

# For the second+ evaluation
MoveEval(HumanPlay,list(HumanLetters),GameBoard,Evaluation)


###--------Benchmark computation------
'''
import cProfile
GameBoard = LoadGame(GameBoard,'Oscar2')
cProfile.run('play("asdflet",GameBoard)',sort=1)
'''

###--------------Output---------------
'''
64473219 function calls in 30.273 seconds
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1   17.047   17.047   30.278   30.278 scrabble2.py:323(BestMove)
  5799517    5.818    0.000    5.818    0.000 {built-in method _bisect.bisect_left}
 46529872    3.724    0.000    3.724    0.000 {method 'isalpha' of 'str' objects}
  5799517    2.011    0.000    7.829    0.000 scrabble2.py:19(binsrch2)
  5799517    0.663    0.000    0.663    0.000 {method 'lower' of 'str' objects}
    24886    0.216    0.000    0.216    0.000 scrabble2.py:178(<listcomp>)
    47709    0.171    0.000    0.387    0.000 scrabble2.py:173(GetWork)
    47595    0.150    0.000    0.580    0.000 scrabble2.py:182(FindAll)
    15254    0.127    0.000    0.947    0.000 scrabble2.py:251(AllGood)
    30294    0.083    0.000    0.083    0.000 {built-in method numpy.core.multiarray.array}
    19409    0.050    0.000    0.053    0.000 scrabble2.py:125(LayAcross)
    10886    0.036    0.000    0.038    0.000 scrabble2.py:135(LayDown)
     1965    0.029    0.000    0.098    0.000 scrabble2.py:294(Score)
     3079    0.017    0.000    0.017    0.000 scrabble2.py:271(Convert)
    63119    0.016    0.000    0.016    0.000 {method 'join' of 'str' objects}
   106301    0.014    0.000    0.014    0.000 {method 'append' of 'list' objects}
    30294    0.012    0.000    0.095    0.000 function_base.py:1461(copy)
    84790    0.011    0.000    0.011    0.000 {built-in method builtins.len}
    15255    0.010    0.000    0.059    0.000 scrabble2.py:142(Layer)
     8342    0.008    0.000    0.008    0.000 scrabble2.py:263(<listcomp>)
      114    0.007    0.000    0.020    0.000 scrabble2.py:237(<listcomp>)
     4733    0.005    0.000    0.005    0.000 scrabble2.py:259(<listcomp>)
     2242    0.005    0.000    0.006    0.000 scrabble2.py:346(<listcomp>)
      114    0.004    0.000    0.007    0.000 scrabble2.py:199(NumGen)
      114    0.004    0.000    0.056    0.000 scrabble2.py:229(BothWays)
     3310    0.004    0.000    0.004    0.000 scrabble2.py:206(TestStart)
      912    0.003    0.000    0.003    0.000 scrabble2.py:299(<listcomp>)
     2939    0.003    0.000    0.003    0.000 scrabble2.py:217(TestEnd)
        7    0.003    0.000    0.006    0.001 scrabble2.py:348(<listcomp>)
     7605    0.003    0.000    0.003    0.000 {method 'count' of 'list' objects}
      114    0.002    0.000    0.002    0.000 scrabble2.py:204(<listcomp>)
      869    0.002    0.000    0.002    0.000 scrabble2.py:315(<listcomp>)
      114    0.002    0.000    0.009    0.000 scrabble2.py:239(<listcomp>)
     1808    0.001    0.000    0.007    0.000 re.py:286(_compile)
       57    0.001    0.000    0.001    0.000 scrabble2.py:233(<listcomp>)
       57    0.001    0.000    0.001    0.000 scrabble2.py:235(<listcomp>)
     1808    0.001    0.000    0.001    0.000 {method 'search' of '_sre.SRE_Pattern' objects}
     1808    0.001    0.000    0.009    0.000 re.py:179(search)
       69    0.001    0.000    0.001    0.000 socket.py:333(send)
        1    0.001    0.001    0.002    0.002 scrabble2.py:150(MoveTiles)
       54    0.001    0.000    0.005    0.000 sre_compile.py:557(compile)
       54    0.001    0.000    0.001    0.000 sre_parse.py:470(_parse)
       54    0.000    0.000    0.002    0.000 sre_parse.py:844(parse)
        1    0.000    0.000    0.001    0.001 {built-in method builtins.sorted}
       54    0.000    0.000    0.001    0.000 sre_compile.py:482(_compile_info)
      108    0.000    0.000    0.001    0.000 enum.py:801(__and__)
        1    0.000    0.000   30.280   30.280 scrabble2.py:410(play)
       54    0.000    0.000    0.000    0.000 sre_parse.py:173(getwidth)
       19    0.000    0.000    0.002    0.000 {built-in method builtins.print}
      181    0.000    0.000    0.000    0.000 scrabble2.py:160(<listcomp>)
      181    0.000    0.000    0.000    0.000 scrabble2.py:161(<listcomp>)
      242    0.000    0.000    0.000    0.000 sre_parse.py:232(__next)
       54    0.000    0.000    0.001    0.000 sre_parse.py:407(_parse_sub)
       54    0.000    0.000    0.000    0.000 sre_parse.py:223(__init__)
      446    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
      216    0.000    0.000    0.000    0.000 enum.py:515(__new__)
      216    0.000    0.000    0.000    0.000 enum.py:265(__call__)
       69    0.000    0.000    0.001    0.000 iostream.py:195(schedule)
       54    0.000    0.000    0.000    0.000 sre_compile.py:64(_compile)
       68    0.000    0.000    0.002    0.000 iostream.py:366(write)
       54    0.000    0.000    0.001    0.000 sre_compile.py:542(_code)
       69    0.000    0.000    0.000    0.000 threading.py:1104(is_alive)
     1445    0.000    0.000    0.000    0.000 scrabble2.py:370(<lambda>)
      181    0.000    0.000    0.000    0.000 scrabble2.py:118(<listcomp>)
       54    0.000    0.000    0.000    0.000 {built-in method _sre.compile}
       54    0.000    0.000    0.000    0.000 sre_parse.py:76(__init__)
      181    0.000    0.000    0.000    0.000 scrabble2.py:121(<listcomp>)
      181    0.000    0.000    0.000    0.000 scrabble2.py:117(ValidVert)
      162    0.000    0.000    0.000    0.000 {built-in method builtins.min}
      181    0.000    0.000    0.000    0.000 scrabble2.py:120(ValidHorz)
      188    0.000    0.000    0.000    0.000 sre_parse.py:171(append)
      108    0.000    0.000    0.000    0.000 sre_compile.py:539(isstring)
       54    0.000    0.000    0.000    0.000 sre_parse.py:828(fix_flags)
      188    0.000    0.000    0.000    0.000 sre_parse.py:253(get)
       54    0.000    0.000    0.000    0.000 sre_compile.py:414(_get_literal_prefix)
       69    0.000    0.000    0.000    0.000 {method 'acquire' of '_thread.lock' objects}
        1    0.000    0.000    0.002    0.002 scrabble2.py:100(DisplayBoard)
       29    0.000    0.000    0.000    0.000 sre_compile.py:393(_generate_overlap_table)
       54    0.000    0.000    0.000    0.000 sre_parse.py:111(__init__)
        1    0.000    0.000   30.281   30.281 {built-in method builtins.exec}
        1    0.000    0.000   30.281   30.281 <string>:1(<module>)
      108    0.000    0.000    0.000    0.000 sre_parse.py:81(groups)
       54    0.000    0.000    0.000    0.000 sre_parse.py:285(tell)
       68    0.000    0.000    0.000    0.000 iostream.py:300(_is_master_process)
       69    0.000    0.000    0.000    0.000 threading.py:1062(_wait_for_tstate_lock)
      362    0.000    0.000    0.000    0.000 {built-in method builtins.any}
       68    0.000    0.000    0.000    0.000 iostream.py:313(_schedule_flush)
      134    0.000    0.000    0.000    0.000 {built-in method builtins.ord}
       54    0.000    0.000    0.000    0.000 sre_parse.py:248(match)
       25    0.000    0.000    0.000    0.000 sre_compile.py:441(_get_charset_prefix)
       69    0.000    0.000    0.000    0.000 iostream.py:93(_event_pipe)
       69    0.000    0.000    0.000    0.000 {method 'append' of 'collections.deque' objects}
       68    0.000    0.000    0.000    0.000 {built-in method posix.getpid}
       54    0.000    0.000    0.000    0.000 {method 'items' of 'dict' objects}
       58    0.000    0.000    0.000    0.000 {method 'extend' of 'list' objects}
        1    0.000    0.000    0.000    0.000 scrabble2.py:105(<listcomp>)
       69    0.000    0.000    0.000    0.000 threading.py:506(is_set)
        1    0.000    0.000    0.000    0.000 scrabble2.py:106(<listcomp>)
        1    0.000    0.000    0.000    0.000 {built-in method numpy.core.multiarray.zeros}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
'''

###--------Very long computation------
'''
import cProfile
GameBoard = LoadGame(GameBoard, 'Oscar2')
BotLetters = list('ker&sgn')
cProfile.run("play(BotLetters,GameBoard)",sort=1)
'''

###---------Output---------
'''
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     27/1  503.582   18.651  880.657  880.657 scrabble2.py:318(BestMove)
150295444  163.796    0.000  163.796    0.000 {built-in method _bisect.bisect_left}
1206144765  120.921    0.000  120.921    0.000 {method 'isalpha' of 'str' objects}
150295444   60.082    0.000  223.878    0.000 scrabble2.py:19(binsrch2)
150295444   19.852    0.000   19.852    0.000 {method 'lower' of 'str' objects}
   242177    2.376    0.000    2.376    0.000 scrabble2.py:177(<listcomp>)
   483039    1.991    0.000    4.367    0.000 scrabble2.py:172(GetWork)
   480075    1.757    0.000    6.576    0.000 scrabble2.py:181(FindAll)
   157411    1.479    0.000   10.645    0.000 scrabble2.py:246(AllGood)
   317493    0.860    0.000    0.860    0.000 {built-in method numpy.core.multiarray.array}
   197859    0.591    0.000    0.621    0.000 scrabble2.py:125(LayAcross)
   119635    0.423    0.000    0.441    0.000 scrabble2.py:135(LayDown)
    21306    0.347    0.000    1.135    0.000 scrabble2.py:289(Score)
   883274    0.233    0.000    0.233    0.000 {method 'join' of 'str' objects}
  1348928    0.189    0.000    0.189    0.000 {method 'append' of 'list' objects}
    30572    0.176    0.000    0.176    0.000 scrabble2.py:266(Convert)
   317493    0.144    0.000    1.004    0.000 function_base.py:1461(copy)
    58292    0.134    0.000    0.175    0.000 scrabble2.py:341(<listcomp>)
   922829    0.131    0.000    0.131    0.000 {built-in method builtins.len}
     2964    0.128    0.000    0.519    0.000 scrabble2.py:233(<listcomp>)
     2964    0.121    0.000    0.219    0.000 scrabble2.py:198(NumGen)
   157412    0.114    0.000    0.692    0.000 scrabble2.py:142(Layer)
    86060    0.114    0.000    0.128    0.000 scrabble2.py:205(TestStart)
     2964    0.108    0.000    1.428    0.000 scrabble2.py:227(BothWays)
    76414    0.098    0.000    0.110    0.000 scrabble2.py:216(TestEnd)
    86980    0.088    0.000    0.088    0.000 scrabble2.py:258(<listcomp>)
      182    0.080    0.000    0.159    0.001 scrabble2.py:343(<listcomp>)
   197730    0.076    0.000    0.076    0.000 {method 'count' of 'list' objects}
     2964    0.055    0.000    0.055    0.000 scrabble2.py:203(<listcomp>)
    51796    0.054    0.000    0.054    0.000 scrabble2.py:254(<listcomp>)
     2964    0.050    0.000    0.288    0.000 scrabble2.py:234(<listcomp>)
    10320    0.038    0.000    0.038    0.000 scrabble2.py:294(<listcomp>)
     1482    0.035    0.000    0.035    0.000 scrabble2.py:232(<listcomp>)
     1482    0.034    0.000    0.034    0.000 scrabble2.py:230(<listcomp>)
    47008    0.032    0.000    0.032    0.000 {method 'search' of '_sre.SRE_Pattern' objects}
    47008    0.029    0.000    0.089    0.000 re.py:179(search)
    47008    0.028    0.000    0.028    0.000 re.py:286(_compile)
       26    0.021    0.001    0.057    0.002 scrabble2.py:150(MoveTiles)
     6511    0.016    0.000    0.016    0.000 scrabble2.py:310(<listcomp>)
     4706    0.009    0.000    0.010    0.000 scrabble2.py:160(<listcomp>)
     4706    0.009    0.000    0.009    0.000 scrabble2.py:161(<listcomp>)
       27    0.007    0.000    0.009    0.000 {built-in method builtins.sorted}
     4706    0.004    0.000    0.004    0.000 scrabble2.py:118(<listcomp>)
     4706    0.004    0.000    0.004    0.000 scrabble2.py:121(<listcomp>)
     4706    0.003    0.000    0.007    0.000 scrabble2.py:117(ValidVert)
     4706    0.003    0.000    0.007    0.000 scrabble2.py:120(ValidHorz)
    15756    0.002    0.000    0.002    0.000 scrabble2.py:365(<lambda>)
     9412    0.002    0.000    0.002    0.000 {built-in method builtins.any}
       69    0.000    0.000    0.000    0.000 socket.py:333(send)
       26    0.000    0.000    0.000    0.000 {built-in method numpy.core.multiarray.zeros}
       69    0.000    0.000    0.001    0.000 iostream.py:195(schedule)
       68    0.000    0.000    0.001    0.000 iostream.py:366(write)
        1    0.000    0.000  880.658  880.658 {built-in method builtins.exec}
       19    0.000    0.000    0.001    0.000 {built-in method builtins.print}
       69    0.000    0.000    0.000    0.000 threading.py:1104(is_alive)
       68    0.000    0.000    0.000    0.000 iostream.py:300(_is_master_process)
       69    0.000    0.000    0.000    0.000 threading.py:1062(_wait_for_tstate_lock)
        1    0.000    0.000    0.001    0.001 scrabble2.py:100(DisplayBoard)
       68    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
       69    0.000    0.000    0.000    0.000 iostream.py:93(_event_pipe)
       26    0.000    0.000    0.000    0.000 {method 'extend' of 'list' objects}
       69    0.000    0.000    0.000    0.000 {method 'acquire' of '_thread.lock' objects}
      182    0.000    0.000    0.000    0.000 scrabble2.py:329(<lambda>)
       68    0.000    0.000    0.000    0.000 iostream.py:313(_schedule_flush)
        1    0.000    0.000  880.658  880.658 scrabble2.py:405(play)
        1    0.000    0.000  880.658  880.658 <string>:1(<module>)
       69    0.000    0.000    0.000    0.000 threading.py:506(is_set)
        1    0.000    0.000    0.000    0.000 scrabble2.py:105(<listcomp>)
       69    0.000    0.000    0.000    0.000 {method 'append' of 'collections.deque' objects}
       68    0.000    0.000    0.000    0.000 {built-in method posix.getpid}
        1    0.000    0.000    0.000    0.000 scrabble2.py:106(<listcomp>)
        1    0.000    0.000    0.000    0.000 {method 'remove' of 'list' objects}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}

'''

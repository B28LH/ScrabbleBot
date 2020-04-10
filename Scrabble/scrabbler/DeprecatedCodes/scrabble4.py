from itertools import permutations as pm
from collections import Counter
from scipy import ndimage
from bisect import bisect_left
from heapq import heappush, heappop
from itertools import count
import numpy as np
import random
import re
import string
import pickle


AddOn = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # For surrounding tiles
WWF = False  # Playing Words With Friends or traditional Scrabble
Small = False  # Small or large board
MaxTile = 7
GameName = 'Oscar2'
Alphabet = string.ascii_letters


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

# Creation of boards
# Notation: *x is double ^x is triple, multiplier can be keyword
# Board: ! is double word, # is triple, ? is start

Official = ['#--*---#', '-!---^--', '--!---*-', '*--!---*', '----!---', '-^---^--', '--*---*-', '#--*---?']
FriendsSmall = ['^-#---', '-*---*', '#-^-*-', '---^--', '--*---', '-*---?']
FriendsBig = ['---#--^-', '--*--!--', '-*--*---', '#--^---!', '--*---*-', '-!---^--', '^---*---', '---!---?']

Official = np.array([list(x) for x in Official])
FriendsSmall = np.array([list(x) for x in FriendsSmall])
FriendsBig = np.array([list(x) for x in FriendsBig])

if WWF:
    file = 'wwf.txt'
    allTileBonus = 35
    startTile = False
    TileValues = WTileValues
    if Small:
        Design = FriendsSmall
    else:
        Design = FriendsBig

else:
    file = 'scra.txt'
    allTileBonus = 50
    startTile = True
    TileValues = STileValues
    Design = FriendsBig

with open(file, 'r') as file:
    words = set(file.read().split())


def AlphaArray(arr):
    return np.isin(arr, list(string.ascii_letters)).astype(int)


def ValidNear(xC, yC):
    t = [(xC + x[0], yC + x[1]) for x in AddOn]
    return [x for x in t if 0 <= x[0] < width and 0 <= x[1] < width]


def ValidVert(xC, yC):
    return [x for x in ((xC + 1, yC), (xC - 1, yC)) if 0 <= x[0] < width and 0 <= x[1] < width]


def ValidHorz(xC, yC):
    return [x for x in ((xC, yC + 1), (xC, yC - 1)) if 0 <= x[0] < width and 0 <= x[1] < width]


class Board:
    def __init__(self, design=Official):  # takes the design and expands it into a full board
        r, c = design.shape
        global width
        self.data = np.pad(design, ((0, r - 1), (0, c - 1)), 'reflect')
        self.alpha = AlphaArray(self.data)
        self.size = width = len(self.data)
        self.design = design

    def __str__(self):
        Indicies = list(map(str, range(self.size)))
        output = ''
        if self.size < 10:
            output += '    ' + '|'.join(Indicies)
        else:
            output += '    ' + '|'.join([x[0] if int(x) > 9 else ' ' for x in Indicies]) + '\n'
            output += '    ' + '|'.join([x[1] if int(x) > 9 else x for x in Indicies]) + '\n'
        for i, x in enumerate(self.data):
            if i < 10: i = str(i) + ' '
            output += str(i) + ' |' + ' '.join(x) + '\n'
        return output

    def __repr__(self):
        return str(self)

    def __setitem__(self, index, value):
        self.data[index] = value
        self.alpha = AlphaArray(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def Layer(self, across, coords, word):
        WordLen = len(word)
        xC, yC = coords
        if across:
            assert yC + WordLen <= self.size, "Too large"
            self.data[xC, yC:yC + WordLen] = list(word)
        else:  # down
            assert xC + WordLen <= self.size, "Too large"
            self.data[xC:xC + WordLen, yC] = list(word)
        self.alpha = AlphaArray(self.data)

# :(
class Tile:
    def __init__(self, parentBoardObj, xC, yC):
        self.xC, self.yC = xC, yC
        self.parent = parentBoardObj

    def __getitem__(self, index):
        return self.parent[index]

    @property
    def alpha(self):
        return self.parent.alpha[self.xC,self.yC]

    def Up(self):
        if self.xC > 0:
            return self.parent[self.xC-1,self.yC]
        else:
            return False

    def Down(self):
        if self.xC < self.parent.size - 1:
            return self.parent[self.xC+1,self.yC]
        else:
            return False

    def Left(self):
        if self.yC > 0:
            return self.parent[self.xC,self.yC-1]
        else:
            return False

    def Right(self):
        if self.yC < self.parent.size - 1:
            return self.parent[self.xC,self.yC+1]
        else:
            return False






def SaveGame(BoardObj, Name=GameName):
    with open('ScrabbleGames/%s.pkl' % Name, 'wb') as f1:
        pickle.dump(BoardObj, f1, pickle.HIGHEST_PROTOCOL)
    print("Game saved as", Name)


def LoadGame(Name=GameName):  ## Watch out for loading a depricated Board object (or just an array)
    with open('ScrabbleGames/%s.pkl' % Name, 'rb') as f:
        LoadBoard = pickle.load(f)
    if type(LoadBoard) == np.ndarray:
        Loader = Board()  # nb set the correct base design
        Loader.data = LoadBoard
        Loader.alpha = AlphaArray(Loader.data)
        LoadBoard = Loader
    print("Game '%s' loaded \n" % Name)
    print(LoadBoard)
    return LoadBoard


def BetterMoveTiles(Board):
    """ Finds the tiles on the board which are adjacent to letter
    (up down left right). If '?' is available, that is selected.
    Returns a array:
        0: No letter borders (or a letter itself)
        1: Vertical border
        2: Horizontal border
        3: Vertical and Horizontal Border
    and a list of the co-ordinates of non-zero cells
    """
    Starters = np.where(Board.data == '?', -1, 0)
    if np.any(Starters):
        return Starters, np.transpose(Starters.nonzero())
    TileLoc = np.isin(Board.data, list(string.ascii_letters)).astype(int)
    Borders = lambda a: np.sum(np.unique(a * np.r_[0, 1, 0, 2, 0, 2, 0, 1, 0]))
    Surround = ndimage.generic_filter(TileLoc, Borders, size=(3, 3), mode='constant')
    Output = (1 - TileLoc) * Surround
    return Output, np.transpose(Output.nonzero())


def WordChain(BoardObj, xC, yC, isVertical):
    """ Returns all neighbouring letters in the specified direction from a given coordinate """
    Alpha = BoardObj.alpha
    Words = BoardObj.data
    if not Alpha[xC, yC]:
        return False
    if isVertical:
        Alpha = np.transpose(Alpha)
        Words = np.transpose(Words)
        xC, yC = yC, xC
    MoverPos = MoverNeg = yC
    while Alpha[xC, MoverPos]:
        MoverPos += 1
        if MoverPos == BoardObj.size:
            break
    while Alpha[xC, MoverNeg]:
        MoverNeg -= 1
        if MoverNeg < 0:
            break
    return Words[xC, MoverNeg+1:MoverPos]











def Distances(BoardObj, Vertical):
    """ If Vertical is True, returns the vertical distances from each cell to
    the nearest letter (from Board.alpha). Else evaluates horizontallly.
    Returns a numpy array the same size as Board.alpha """
    DistBoard = np.copy(BoardObj.alpha)
    queue = []
    c = count()
    if Vertical:
        BorderCells = ValidVert
    else:
        BorderCells = ValidHorz

    Letters = np.transpose(np.where(DistBoard))  # All existing letter indices
    for index in Letters:
        heappush(queue, (1, next(c), index, None))  # Adds letters to queue
    while queue:
        value, __, index, parents = heappop(queue)
        for neighbour in BorderCells(index[0], index[1]):
            if (DistBoard != 0)[neighbour]:  # check that the cell hasn't been covered yet
                continue
            heappush(queue, (value + 1, next(c), neighbour, index))
            DistBoard[neighbour] = value + 1
    return DistBoard - 1


NewGame = LoadGame()
BetterMoveTiles(NewGame)
print(Distances(NewGame, True))

'''

###---------Under Development--------
def GetWork(row, col, GameBoard, Across): #Returns Workspace and start (entire row/columm)
    if Across: return (GameBoard[row,:], col)
    else: return (GameBoard[:,col],row)


def FindAll(Board, row, col, across): #Across = False means vert
    Workspace, Start = Board.provide(row, col, across)
    initial = Workspace[Start]
    if initial.isalpha():
        output = [initial]
    else:
        output = ['.']
    Second = Start + 1
    Start -= 1
    while Start >= 0 and (Workspace[Start].isalpha() or Workspace[Start] in ['.','?']):
        output = [Workspace[Start]] + output
        Start -= 1
    while Second < width and (Workspace[Second].isalpha() or Workspace[Second] in ['.','?']):
        output.append(Workspace[Second])
        Second += 1
    return (''.join(output), Start+1)

def NumGen(Length, Pos):
    AllPos = []
    for i in range(1,Length+2):
        for x in range(Length-i+1):
            AllPos.append((x,x+i))
    return [x for x in AllPos if x[0] <= Pos < x[1]]

def TestStart(item, GameBoard):
    if not item[0][0].isalpha():
        xC, yC = item[1][1][0], item[1][1][1]
        if item[1][0] == 1:
            xC -= 1
        else:
            yC -= 1
        if xC >= 0 and yC >= 0 and GameBoard[xC][yC].isalpha():
            return False
    return True

def TestEnd(item, GameBoard):
    if not item[0][-1].isalpha():
        xC, yC = item[1][2][0], item[1][2][1]
        if item[1][0] == 1:
            xC += 1
        else:
            yC += 1
        if xC < width and yC < width and GameBoard[xC][yC].isalpha():
            return False
    return True

def BothWays(row, col, Board, i, MoveBoard, length):#1 = Vert, 2 = Horz
    Work, Pos = GetWork(row, col, GameBoard, i==2)
    if i == 1: #Vertical
        Splits = [(Work[a:b],(i,(a,col),(b,col))) for a,b in NumGen(len(Work),Pos)]
    else: #Horizontal
        Splits = [(Work[a:b],(i,(row,a),(row,b))) for a,b in NumGen(len(Work),Pos)]
    Splits = [x for x in Splits if [y.isalpha() for y in x[0]].count(0) <= length and len(x[0]) > 1]
    Splits = [x for x in Splits if TestStart(x, GameBoard) and TestEnd(x, GameBoard)]
    Result = MoveBoard[row][col]
    Truth = FindAll(row, col, GameBoard, i==2)[0]
    Real = []
    if Result == 3 or Result == i:
        for item in Splits:
            if re.search(Truth,''.join(item[0])):
                Real.append(item)
        return Real
    else:
        return Splits

def AllGood(Direction, Start, Word, GameBoard):
    Tester = np.copy(GameBoard)
    Layer(Direction,Start[0],Start[1],Word,Tester)
    if not binsrch2(words,FindAll(Start[0],Start[1],Tester,Direction==2)[0].lower()):
        return False
    attemptBoard = np.copy(GameBoard)
    if Direction == 1:
        OpDir = 2
        AllTiles = [(Start[0]+i,Start[1]) for i in range(len(Word))]
        LayDown(Start[0],Start[1],Word,attemptBoard)
    else:
        OpDir = 1
        AllTiles = [(Start[0],Start[1]+i) for i in range(len(Word))]
        LayAcross(Start[0],Start[1],Word,attemptBoard)
    for r,c in AllTiles:
        Others = FindAll(r,c,attemptBoard,OpDir == 2)[0]
        if len(Others) > 1 and not binsrch2(words,Others.lower()):
            return False
    return True

def Convert(Word,Behind):
    Output = 0
    Multiplier = 1
    if startTile:
        accept = ['!','?']
    else:
        accept = ['!']
    for i, char in enumerate(Word):
        if Behind[i] == '*':
            Output += 2*TileValues[char]
        elif Behind[i] == '^':
            Output += 3*TileValues[char]
        elif Behind[i] in accept:
            Multiplier *= 2
            Output += TileValues[char]
        elif Behind[i] == '#':
            Multiplier *= 3
            Output += TileValues[char]
        else:
            Output += TileValues[char]
    return Output*Multiplier


def Score(Direction,Start,Word,GameBoard,AllUsed,MoveBoard):
    total = 0
    newBoard = np.copy(GameBoard)
    if Direction == 1:
        LayDown(Start[0],Start[1],Word,newBoard)
        under = [GameBoard[Start[0]+i][Start[1]] for i in range(len(Word))]
    else:
        LayAcross(Start[0],Start[1],Word,newBoard)
        under = GameBoard[Start[0]][Start[1]:Start[1]+len(Word)]
    total += Convert(Word,under)
    for i in range(len(Word)):
        if Direction == 1:
            r,c = Start[0]+i,Start[1]
            OpDir = True
        else:
            r,c = Start[0],Start[1]+i
            OpDir = False
        if not GameBoard[r][c].isalpha() and MoveBoard[r][c] != 0:
            alt = FindAll(r,c,newBoard,OpDir)
            if len(alt[0]) > 1:
                if Direction == 2:
                    under = [GameBoard[alt[1]+i][c] for i in range(len(alt[0]))]
                else:
                    under = GameBoard[r][alt[1]:alt[1]+len(alt[0])]
                total += Convert(alt[0],under)
    if AllUsed:
        total += allTileBonus
    return total


def BestMove(Tiles, Board):
    ### Fix?
    if '&' in Tiles:
        alternate = list(Tiles)
        alternate.remove('&')
        master = []
        for item in Alphabet:
            newTiles = alternate + [item]
            a = BestMove(newTiles,Board)[-7:]
            if a:
                master.extend(a)
        if len(master) > 0:
            return sorted(master, key=lambda x: x[-1])
        return False
    ##
    Moves = []
    MoveBoard, GoodTiles = BetterMoveTiles(Board)
    SolvedCases = {}
    for row,col in GoodTiles:
        Section = []
        for i in (1,2):
            for item in BothWays(row,col,GameBoard,i,MoveBoard,len(Tiles)):
                Section.append(item)
        for item in Section:
            valids = []
            fills = [x.isalpha() for x in item[0]].count(0)
            if fills not in SolvedCases:
                SolvedCases[fills] = list(set([''.join(x) for x in list(set(pm(Tiles,fills)))]))
            for part in SolvedCases[fills]:
                a, attempt = 0, ''
                for char in item[0]:
                    if char.isalpha():
                        attempt += char
                    else:
                        attempt += part[a]
                        a += 1
                if binsrch2(words, attempt.lower()):
                    if a == MaxTile:
                        valids.append((attempt,True))
                    else:
                        valids.append((attempt,False))
            for piece in valids:
                if AllGood(item[1][0],item[1][1],piece[0],GameBoard):
                    Start = item[1][1]
                    Direction = item[1][0]
                    Points = Score(Direction,Start,piece[0],GameBoard,piece[1],MoveBoard)
                    Assembly = (Direction,Start,piece[0],Points)
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
        BMP = BestMove(let,GameBoard)
        if BMP:
            BMP = BMP[-1]
            Layer(BMP[0],BMP[1][0],BMP[1][1],BMP[2],GameBoard)
            print("\n\nWith letters %s,\nI play %s for %i points\n" % (' '.join(let),BMP[2],BMP[3]))
            if Moves % 2 == 0:
                Comp1 += BMP[3]
                print("Comp1's move")
            else:
                print("Comp2's move")
                Comp2 += BMP[3]
            print("Scores:\n\tComp1: %i\n\tComp2: %i" % (Comp1,Comp2))
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
        print(key+'')
        for num,definition in enumerate(Meaning[key]):
            print('\t%i %s' % (num+1, definition))

def play(MyLetters,GameBoard):
    TheMoves = BestMove(MyLetters,GameBoard)
    if TheMoves:
        MyMove = TheMoves[-1]
        print("I play %s for %i points\n" % (MyMove[2],MyMove[3]))
        Layer(MyMove[0],MyMove[1][0],MyMove[1][1],MyMove[2],GameBoard)
        DisplayBoard(GameBoard)
        print(list(reversed(TheMoves[-10:]))) #Do I need to print all the other options?
        DisplayMeaning(MyMove[2])
    else:
        print("With letters %s,\nI cannot play a move" % (' '.join(MyLetters)))

def InputFormat(string,GameBoard):
    trans = string.split()
    if trans[0] == 'd':
        Dir = 1
    else:
        Dir = 2
    row, col = int(trans[1]),int(trans[2])
    word = trans[3]
    MB = MoveTiles(GameBoard)[0]
    return (Dir, (row,col),word, MB)

def isWord(word):
    print(binsrch2(words,word.lower()))

def MoveEval(Word,Tiles,GameBoard,CompMoves):
    testGame = np.copy(GameBoard)
    Dir, Start, word, MB = InputFormat(Word,testGame)
    if not CompMoves:
        CompMoves = BestMove(Tiles,GameBoard)
    MyMove = (Dir,Start,word,Score(Dir,Start,word,GameBoard,False,MB))
    for i,x in enumerate(CompMoves):
        if x == MyMove:
            maxScore = CompMoves[-1][-1]
            total = len(CompMoves)
            print("Playing %s for %i points:" % (MyMove[2],MyMove[-1]))
            print("\t{}% of possible points".format(round(MyMove[-1]*100/maxScore,2)))
            print("\tWord %i out of %i" % (total-i,total))
            break
    else:
        print("Not a valid word")
    return CompMoves

def CheckInput(initial,GameBoard,Play):
    Dir, Start, word, MB = InputFormat(initial,GameBoard)
    if Dir == 1:
        CovSquare = [(Start[0]+i,Start[1]) for i in range(len(word))]
    else:
        CovSquare = [(Start[0],Start[1]+i) for i in range(len(word))]
    for x,(r,c) in enumerate(CovSquare):
        if GameBoard[r][c].isalpha() and GameBoard[r][c] != word[x]:
            print("Not a valid move")
            return False
    if AllGood(Dir,Start,word,GameBoard):
        print("\n%s scores %i points\n" % (word,Score(Dir,Start,word,GameBoard,False,MB)))
        if Play:
            Layer(Dir,Start[0],Start[1],word,GameBoard)
            DisplayBoard(GameBoard)
    else:
        print("Not a valid move")

###---------Area to play in------------####


#Wipe GameBoard
GameBoard = np.copy(StartBoard)

#Show the game
DisplayBoard(GameBoard)

#Save the game, name defaults to GameName
SaveGame(GameBoard)

#Load a previous game. Second variable is the name of the file (optional)
GameBoard = LoadGame(GameBoard)

#Check if a word is valid
isWord('ia')

# Lookup word in dictionary
DisplayMeaning("kai")

# Check to see if a given play is valid: CheckInput(initial,GameBoard,Play)
# initial is a move string ('d 5 6 rosey' (row,column))
# GameBoard is the board
# Play is True when you want the move to be entered, False if just check
Choice = 'a 2 1 roam'
CheckInput(Choice,GameBoard,True)


# Computer's letters (a blank is denoted by &)
BotLetters = list('yifighi')

# Ask the Computer to play a move
play(BotLetters,GameBoard)



# Ranking a human move
HumanLetters = 'yifighi'
HumanPlay = 'a 11 7 jet'

# Creates a move evaluation (for first time)
Evaluation = MoveEval(HumanPlay,list(HumanLetters),GameBoard,False)

# For the second+ evaluation
MoveEval(HumanPlay,list(HumanLetters),GameBoard,Evaluation)

#Letters to try: 'r&qotia'
'''
###---------Runtime data from scrabble2--------
'''
from a blank on Oscar2
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

###-------------Deprecated functions--------------
# Finds the possible start tiles, returns a board and a list
# 3 means both, 2 is vertical, 1 is horizontal, 0 is none, -1 is start

def MoveTiles(Board):
    global width
    width = len(Board)
    StartingSquares = np.zeros((width,width))
    StartTilesList = []
    wid = range(width)
    for xC in wid:
        for yC in wid:
            if Board[xC,yC] == ',':
                StartingSquares[xC,yC] = -1
                return (StartingSquares, [(xC,yC)])
            elif not Board[xC,yC].isalpha():
                Vertical = any([Board[x1,y1].isalpha() for x1,y1 in ValidVert(xC,yC)])
                Horizontal = any([Board[x1,y1].isalpha() for x1,y1 in ValidHorz(xC,yC)])
                if Vertical or Horizontal:
                    StartTilesList.append((xC,yC))
                if Vertical and Horizontal:
                    StartingSquares[xC,yC] = 3
                elif Horizontal:
                    StartingSquares[xC,yC] = 2
                elif Vertical:
                    StartingSquares[xC,yC] = 1
    return (StartingSquares, StartTilesList)


# Timing BetterMoveTiles
def QuadFlip(design):
    r,c = design.shape
    return np.pad(design,((0,r-1),(0,c-1)),'reflect')

Official[1:7,2] = list('random')
Official
BigFlip = np.copy(Official)
i = 12
for _ in range(i):
    BigFlip = QuadFlip(BigFlip)
BoardBig = Board(BigFlip)
#cProfile.run('MoveTiles(BoardBig.data)',sort=1)
cProfile.run('BetterMoveTiles(BoardBig)',sort=1)


'''

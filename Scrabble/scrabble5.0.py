from scipy import ndimage
import numpy as np
import string
import pickle
from helpers import core


# Todo:
# Implement new dictionary and word checker
# Implement playing against computer
# Work through best move
# Create move object
# New way to find all possible places to play

# Is alpha

# EngDict = PyDictionary()

AddOn = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # For surrounding tiles
WWF = False  # Playing Words With Friends or traditional Scrabble
Small = False  # Small or large board
MaxTile = 7
GameName = 'Oscar2'
Alphabet = string.ascii_letters




def ValidNear(xC, yC):
    t = [(xC + x[0], yC + x[1]) for x in AddOn]
    return [x for x in t if 0 <= x[0] < width and 0 <= x[1] < width]


def ValidVert(xC, yC):
    return [x for x in ((xC + 1, yC), (xC - 1, yC)) if 0 <= x[0] < width and 0 <= x[1] < width]


def ValidHorz(xC, yC):
    return [x for x in ((xC, yC + 1), (xC, yC - 1)) if 0 <= x[0] < width and 0 <= x[1] < width]


def AlphaArray(arr):
    return np.isin(arr, list(string.ascii_letters)).astype(int)


# class Move():
#    def __init__(self,start,end,word)




NewGame = LoadGame()


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

def BetterMoveTiles(Board):
    """ Finds the tiles on the board which are adjacent to letter
    (up down left right). If '?' is availible, that is selected.
    Returns a array:
        0: No letter borders (or a letter itself)
        1: Vertical border
        2: Horizontal border
        3: Vertical and Horizontal Border
    and a list of the co-ordinates of non-zero cells
    """
    Starters = np.where(Board.data == '?', -1, 0)
    if np.any(Starters):
        return (Starters, np.transpose(Starters.nonzero()))
    TileLoc = np.isin(Board.data, list(string.ascii_letters)).astype(int)
    Borders = lambda a: np.sum(np.unique(a * np.r_[0, 1, 0, 2, 0, 2, 0, 1, 0]))
    Surround = ndimage.generic_filter(TileLoc, Borders, size=(3, 3), mode='constant')
    Output = (1 - TileLoc) * (Surround)
    return (Output, np.transpose(Output.nonzero()))


BetterMoveTiles(NewGame)

###-------

from heapq import heappush, heappop
from itertools import count


def Distances(Board, Vertical):
    """
    If Vertical is True, returns the vertical distances from each cell to
    the nearest letter (from Board.alpha). Else evaluates horizontallly.
    Returns a numpy array the same size as Board.alpha
    """
    DistBoard = np.copy(Board.alpha)
    queue = []
    c = count()
    if Vertical:
        BorderCells = ValidVert
    else:
        BorderCells = ValidHorz

    Letters = np.transpose(np.where(DistBoard))  # All existing letter indicies
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


V = Distances(NewGame, True)
H = Distances(NewGame, False)

######################################################


'''

###---------Under Development--------
def GetWork(row, col, GameBoard, Across): #Returns Workspace and start (entire row/columm)
    if Across:
        Workspace = list(GameBoard[row])
        Start = col
    else:
        Workspace = list(GameBoard[:,col])
        Start = row
    return (Workspace,Start)

def FindAll(row, col, GameBoard, Across): #Across = False means vert
    Workspace, Start = GetWork(row, col, GameBoard, Across)
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

def NumGen(Length, Pos): #Provides all possible subsets of from a position
    AllPos = []
    for i in range(1,Length+2):
        for x in range(Length-i+1):
            AllPos.append((x,x+i))
    return [x for x in AllPos if x[0] <= Pos < x[1]]

def TestStart(item, GameBoard):
    if not item[0][0].isalpha():
        xCord, yCord = item[1][1][0], item[1][1][1]
        if item[1][0] == 1:
            xCord -= 1
        else:
            yCord -= 1
        if xCord >= 0 and yCord >= 0 and GameBoard.alpha[xCord,yCord]:
            return False
    return True

def TestEnd(item, GameBoard):
    if not item[0][-1].isalpha():
        xCord, yCord = item[1][2][0], item[1][2][1]
        if item[1][0] == 1:
            xCord += 1
        else:
            yCord += 1
        if xCord < width and yCord < width and GameBoard.alpha[xCord,yCord]:
            return False
    return True

#All possible places to play from a given r,c and length
def BothWays(row, col, GameBoard, i, MoveBoard, length):#1 = Vert, 2 = Horz
    Work, Pos = GetWork(row, col, GameBoard, i==2)
    if i == 1: #Vertical
        # Returns all possible play tiles (i.e -*p-), their orientation and start and end points
        Splits = [(Work[a:b],(i,(a,col),(b,col))) for a,b in NumGen(len(Work),Pos)]
    else: #Horizontal
        Splits = [(Work[a:b],(i,(row,a),(row,b))) for a,b in NumGen(len(Work),Pos)]
    #Ensures all splits contains a letter    
    Splits = [x for x in Splits if [y.isalpha() for y in x[0]].count(0) <= length and len(x[0]) > 1]
    #ensures that the start and end aren't next to a filled in tile
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
    Tester = np.copy(GameBoard.data)
    Layer(Direction,Start[0],Start[1],Word,Tester)
    if not isWord(FindAll(Start[0],Start[1],Tester,Direction==2)[0].lower()):
        return False
    attemptBoard = copy.deepcopy(GameBoard)
    if Direction == 1:
        OpDir = 2
        AllTiles = [(Start[0]+i,Start[1]) for i in range(len(Word))]
        attemptBoard.Layer(2,Start,Word)
    else:
        OpDir = 1
        AllTiles = [(Start[0],Start[1]+i) for i in range(len(Word))]
        attemptBoard.Layer(1,Start,Word)
    for r,c in AllTiles:
        Others = FindAll(r,c,attemptBoard,OpDir == 2)[0]
        if len(Others) > 1 and not isWord(Others.lower()):
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
        under = [GameBoard[Start[0]+i,Start[1]] for i in range(len(Word))]
    else:
        LayAcross(Start[0],Start[1],Word,newBoard)
        under = GameBoard[Start[0],Start[1]:Start[1]+len(Word)]
    total += Convert(Word,under)
    for i in range(len(Word)):
        if Direction == 1:
            r,c = Start[0]+i,Start[1]
            OpDir = True
        else:
            r,c = Start[0],Start[1]+i
            OpDir = False
        if not GameBoard.alpha[r,c] and MoveBoard[r,c] != 0:
            alt = FindAll(r,c,newBoard,OpDir)
            if len(alt[0]) > 1:
                if Direction == 2:
                    under = [GameBoard[alt[1]+i,c] for i in range(len(alt[0]))]
                else:
                    under = GameBoard[r,alt[1]:alt[1]+len(alt[0])]
                total += Convert(alt[0],under)
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
            a = BestMove(newTiles,GameBoard)[-7:]
            if a:
                master.extend(a)
        if len(master) > 0:
            return sorted(master, key=lambda x: x[-1])
        return False
    Moves = []
    MoveBoard, GoodTiles = BetterMoveTiles(GameBoard)
    SolvedCases = {}
    for row,col in GoodTiles:
        Section = []
        for i in (1,2):
            for item in BothWays(row,col,GameBoard,i,MoveBoard,len(Tiles)):
                Section.append(item)
        for item in Section:
            valids = []
            fills = [x.isalpha() for x in item[0]].count(0) #number of blanks in selection
            if fills not in SolvedCases: #generates new permuations
                SolvedCases[fills] = list(set([''.join(x) for x in list(set(pm(Tiles,fills)))]))
            for part in SolvedCases[fills]: #building out the new word
                a, attempt = 0, ''
                for char in item[0]:
                    if char.isalpha():
                        attempt += char
                    else:
                        attempt += part[a]
                        a += 1
                if isWord(attempt.lower()):
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
        GameBoard.Layer(MyMove[0],MyMove[1],MyMove[2])
        print(GameBoard)
        print(list(reversed(TheMoves[-10:]))) #Do I need to print all the other options?
        #DisplayMeaning(MyMove[2])
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
    MB = BetterMoveTiles(GameBoard)[0]
    return (Dir, (row,col),word, MB)

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
        if GameBoard.alpha[r,c] and GameBoard[r,c] != word[x]:
            print("Not a valid move")
            return False
    if AllGood(Dir,Start,word,GameBoard):
        print("\n%s scores %i points\n" % (word,Score(Dir,Start,word,GameBoard,False,MB)))
        if Play:
            GameBoard.Layer(Dir,Start,word)
            print(GameBoard)
    else:
        print("Not a valid move")

import cProfile
NewGame = LoadGame('Oscar2')
cProfile.run('play("asdflet",NewGame)',sort=1)

###---------Area to play in------------####


# Wipe GameBoard
GameBoard = np.copy(StartBoard)

# Show the game
DisplayBoard(GameBoard)

# Save the game, name defaults to GameName
SaveGame(GameBoard, 'Oscar1')

# Load a previous game. Second variable is the name of the file (optional)
GameBoard = LoadGame(GameBoard, 'Oscar2')

# Check if a word is valid
isWord('oiler')

# Lookup word in dictionary
DisplayMeaning("neuritis")

# Check to see if a given play is valid: CheckInput(initial,GameBoard,Play)
# initial is a move string ('d 5 6 rosey' (row,column))
# GameBoard is the board
# Play is True when you want the move to be entered, False if just check
Choice = 'a 14 1 kerns'
CheckInput(Choice, GameBoard, True)
# Computer's letters (a blank is denoted by &)
BotLetters = list('kernsgn')

# Ask the Computer to play a move
# play(BotLetters,GameBoard)


# Ranking a human move
HumanLetters = 'yifighi'
HumanPlay = 'a 11 7 jet'

# Creates a move evaluation (for first time)
Evaluation = MoveEval(HumanPlay, list(HumanLetters), GameBoard, False)

# For the second+ evaluation
MoveEval(HumanPlay, list(HumanLetters), GameBoard, Evaluation)


'''

###------------Dump---------
'''
###-------OLD
for char in Alphabet:
    TileValues[char] = 0

def Refresh():
    global TileBag
    TileBag = list(Counter(bagamts).elements())
    random.shuffle(TileBag)

def TakeTiles(numb): #Could definitely clean this up
    random.shuffle(TileBag)
    numb = min(numb,len(TileBag))
    out = []
    for i in range(numb):
        out.append(TileBag.pop())
    return out

###-------OLD
def MoveTiles(GameBoard):
    StartingSquares = np.zeros((width,width))
    StartTilesList = []
    wid = range(width)
    for xCord in wid:
        for yCord in wid:
            if GameBoard[xCord][yCord] == '?':
                StartingSquares[xCord][yCord] = -1
                return (StartingSquares, [(xCord,yCord)])
            elif not GameBoard[xCord][yCord].isalpha():
                Vertical = any([GameBoard[x1][y1].isalpha() for x1,y1 in ValidVert(xCord,yCord)])
                Horizontal = any([GameBoard[x1][y1].isalpha() for x1,y1 in ValidHorz(xCord,yCord)])
                if Vertical or Horizontal:
                    StartTilesList.append((xCord,yCord))
                if Vertical and Horizontal:
                    StartingSquares[xCord][yCord] = 3
                elif Horizontal:
                    StartingSquares[xCord][yCord] = 2
                elif Vertical:
                    StartingSquares[xCord][yCord] = 1
    return (StartingSquares, StartTilesList)
    

def DisplayBoard(grid):
    h = range(len(grid))
    if len(grid) < 10:
        print('    '+'|'.join(map(str,h)))
    else:
        print('    '+'|'.join([x[0] if int(x) > 9 else ' ' for x in map(str,h)]))
        print('    '+'|'.join([x[1] if int(x) > 9 else x for x in map(str,h)]))
    for i,x in enumerate(grid):
        if i < 10: i = str(i)+' '
        print(i,'|'+ ' '.join(x))

DisplayBoard(StartBoard)

def SaveGame(GameBoard, Name=GameName):
    with open('ScrabbleGames/%s.pkl' % Name,'wb') as f1:
        pickle.dump(GameBoard, f1, pickle.HIGHEST_PROTOCOL)
    print("Game saved as",Name)

def LoadGame(Name=GameName):
    with open('ScrabbleGames/%s.pkl' % Name,'rb') as f:
        GameBoard = pickle.load(f)
    print("Game '%s' loaded" % Name)
    print(GameBoard)
    return GameBoard
'''

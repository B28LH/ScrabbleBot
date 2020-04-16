from scrabbler.major import core, data, algo
from copy import deepcopy
import numpy as np
import random


def isWord(word):
    return word in data.wordset


def meaning(word):
    if not isWord(word):
        return "Not a word"
    return data.meaningDict[word]


def newBag():
    bag = []
    for key, value in data.bagamts.items():
        bag.extend([key] * value)


def drawTiles(numTiles):
    rack = []
    random.shuffle(data.bag)
    i = 0
    while len(data.bag) > 0 and i < numTiles:
        rack.append(data.bag.pop())
        i += 1
    return rack


def playMove(rack, boardObj, handicap=1):
    """ The main interface for invoking a bot move, returns a lists of moves and places the selected

    :param rack: the (usually 7 letter) iterable (string or list) of letters with which the bot plays
    :param boardObj: the board, a Board() object
    :param handicap: the percentile of the selected move from all move (1 is the best, 0.5 is half way etc.)
        suggested handicap is 0.97
    :return a list of Move() objects in sorted order
    """
    theMoves = algo.allMoves(rack, boardObj)
    print(boardObj)
    if len(theMoves) > 0:
        if handicap == 1:
            myMove = theMoves[-1]
        else:
            myMove = theMoves[int(len(theMoves) * handicap)]
        print(f"\nI play {myMove}:")
        boardObj.layerMoveObj(myMove)
        print(f"{myMove.word}: {meaning(myMove.word)}")
    else:
        print("I cannot play a move :(")
    return theMoves


def castMove(moveStr, boardObj=data.gameBoard):
    """ A slightly easier interface for inserting words into a board

    :param moveStr: a string in the from '[a/d] rowNum colNum word', where a/d is across/down
    :param boardObj: defaults to data.gameBoard
    """
    direction, row, col, word = moveStr.split()
    moveObj = core.Move(word, (row, col), boardObj, across=(direction == 'a'))
    boardObj.layer(moveObj)


def virtualGame(handicap=1):  # TODO: Human interaction
    """ WORK IN PROGRESS: Play a game against the machine without a real board"""
    gb = data.gameBoard = core.Board()
    while True:
        humanTiles = drawTiles(7)
        print(f"Your rack:")
        for char in humanTiles:
            print(f"{char}: {data.sTileValues[char]}")
        while True:
            response = input("Action? [Type H for help]: ")
            if response is not None:
                args = response.split()
                command = args[0][0].upper()
                if command == 'P':
                    pass
                    break
                    # TODO: make user evaluation
                elif command == 'D':
                    print(f"{args[1]}: {meaning(args[1])}")
                elif command == 'S':
                    random.shuffle(humanTiles)
                elif command == 'H':
                    for key, value in data.humanActions.items():
                        print(key, value)
                elif command == 'K' and len(args) > 1:
                    data.gameBoard.save(saveName=args[1], display=True)
                elif command == 'Q':
                    quit()
        botLetters = drawTiles(7)
        playMove(botLetters, data.gameBoard, handicap=handicap)

# DEVELOPMENT:

# def analyseMove(theMoves):
#     """ A wrapper for playMove that finds percentiles"""
#     scores = np.array([x.score for x in theMoves])
#     for i in range(20):
#         i /= 5
#         print(i, scores.std() + i * scores.mean())
#     for i in range(90, 100):
#         i /= 100
#         print(i, theMoves[int(len(theMoves) * i)].score)


# def playBlank(tiles, boardObj=data.gameBoard):
#     realBests = []
#     for char in data.loweralpha:
#         print("Trying: ", char)
#         realBests.extend(algo.allMoves(tiles + char, deepcopy(boardObj)))
#     realBests.sort()
#     return realBests

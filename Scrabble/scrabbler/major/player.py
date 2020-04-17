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


def checkHumanWord(word, startRow, startCol, remainingTiles, boardObj):
    """ When given a word, checks that the word can be played given the board and tiles

    :param word: the word you are playing
    :param startRow: the row of the leftmost tile
    :param startCol: the column of the leftmost tile
    :param remainingTiles: the tiles you can play with
    :param boardObj: the Board() object
    :return: True if the word can be played, false if not
    """
    boardObj.cachedAlpha = boardObj.alpha
    data.crossed = algo.crossChecks(boardObj)
    wordLen = len(word)
    if startCol + wordLen >= boardObj.size:  # Check if the word will go over the board
        return False
    elif word not in data.wordset:  # This might not be needed
        return False
    leftTile = algo.posMove(startRow, startCol, across=True)
    if leftTile is not None and boardObj.cachedAlpha[leftTile]:  # Checks if right is not clear.
        return False
    rightTile = algo.negMove(startRow, startCol + wordLen, boardObj.size)
    if rightTile is not None and boardObj.cachedAlpha[rightTile]:  # Checks if right is not clear.
        return False
    i = 0
    letters = list(remainingTiles)
    while i < wordLen:
        crossStatus = data.crossed[startRow][startCol + i]  # Crossed should be in data
        if crossStatus:
            if crossStatus == "I":
                return False
            elif crossStatus != "C" and word[i] not in crossStatus:
                return False
            elif word[i] not in letters:
                return False
            letters.remove(word[i])
        else:
            if boardObj.squares[startRow, startCol + i] != word[i]:
                return False
        i += 1
    return letters


def printTiles(humanTiles):
    print(f"Your rack: {''.join(humanTiles)}")
    for char in humanTiles:
        print(f"{char}: {data.sTileValues[char]}")


def virtualGame(handicap=1):  # TODO: Keep track of scores
    """ WORK IN PROGRESS: Play a game against the machine without a real board"""
    gb = data.gameBoard = core.Board()
    humanTiles = drawTiles(7)
    humanScore = 0
    botScore = 0
    while True:
        humanTiles.extend(drawTiles(7 - len(humanTiles)))
        printTiles(humanTiles)
        while True:
            response = input("Action? [Type H for help]: ")
            if response is not None:
                args = response.split()
                command = args[0][0].upper()
                if command in ('P', 'C'):
                    _, direction, row, col, word = args
                    row, col = int(row), int(col)
                    humanMove = core.Move(word, (row, col), gb, direction == 'a')
                    if direction == 'd':
                        flippedBoard = deepcopy(data.gameBoard)
                        flippedBoard.squares = flippedBoard.squares.transpose()
                        validity = checkHumanWord(word, col, row, humanTiles, flippedBoard)
                    else:
                        validity = checkHumanWord(word, row, col, humanTiles, data.gameBoard)
                    if validity:
                        print(str(humanMove))
                        if command == 'P':
                            data.gameBoard.layerMoveObj(humanMove)
                            humanTiles = list(validity)
                            humanScore += humanMove.score
                            break
                    else:
                        print("Not a valid move")
                elif command == 'D':
                    print(f"{args[1]}: {meaning(args[1])}")
                elif command == 'S':
                    random.shuffle(humanTiles)
                    printTiles(humanTiles)
                elif command == 'H':
                    for key, value in data.humanActions.items():
                        print(key, value)
                elif command == 'B':
                    print(data.gameBoard)
                elif command == 'K' and len(args) > 1:
                    data.gameBoard.save(saveName=args[1])
                elif command == 'Q':
                    quit()
        botLetters = drawTiles(7)  # The bot shouldn't get 7 new tiles each round.
        print(f"BotLetters: {''.join(botLetters)}")
        answer = playMove(botLetters, data.gameBoard, handicap=handicap)[-1]
        botScore += answer.score
        print(f"BotScore: {botScore}, HumanScore: {humanScore}")

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

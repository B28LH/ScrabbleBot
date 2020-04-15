from scrabbler.major import core, data, algo
import numpy as np


def isWord(word):
    return word in data.wordset


def meaning(word):
    assert isWord(word), "Not a word"
    return data.meaningDict[word]


def playMove(rack, boardObj, handicap=1):
    """ The

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
    """ slightly easier interface for inserting words into a board

    :param moveStr: a string in the from '[a/d] rowNum colNum word', where a/d is across/down
    :param boardObj: defaults to data.gameBoard
    """
    direction, row, col, word = moveStr.split()
    moveObj = core.Move(word, (row, col), boardObj, across=(direction == 'a'))
    boardObj.layer(moveObj)


def analyseMove(theMoves):
    """ A wrapper for playMove that finds percentiles"""
    scores = np.array([x.score for x in theMoves])
    for i in range(20):
        i /= 5
        print(i, scores.std() + i * scores.mean())
    for i in range(90, 100):
        i /= 100
        print(i, theMoves[int(len(theMoves) * i)].score)

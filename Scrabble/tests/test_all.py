import cProfile

import numpy as np
import pytest

from scrabbler.major import core, data, algo, player
from scrabbler.oldCodes import scrabblerOLDWRAPPED


def translatePlay(tiles, boardObj):
    result = sorted(scrabblerOLDWRAPPED.BestMove(tiles, boardObj.squares), key=lambda x: x[-1])
    return [core.Move(x[2], x[1], boardObj, score=x[3]) for x in result if x[0] == 2]


@pytest.fixture
def my_board():
    data.gameBoard = core.load('ThreeWords')
    return data.gameBoard


@pytest.fixture
def my_letters():
    return 'trial'


def test_crossCheck(my_board):
    assert algo.crossChecks(my_board)[5][5] is "I"
    assert algo.crossChecks(my_board)[9][6] is "C"
    assert algo.crossChecks(my_board)[9][5] is None
    assert isinstance(algo.crossChecks(my_board)[11][5], type(set()))


def test_checkWordMatches(my_board):
    assert algo.checkWordMatches(3, 'amia', 9, 4, 'amia', my_board)
    assert algo.checkWordMatches(2, 'tear', 12, 10, 'tear', my_board)
    assert algo.checkWordMatches(2, 'omen', 8, 10, 'omen', my_board)
    # assert algo.checkWordMatches(2, 'erm', 10, 4, 'erm', my_board)
    # Insufficient tiles in rack:
    assert not algo.checkWordMatches(2, 'omen', 8, 10, 'not', my_board)
    # Right collision at end of word
    assert not algo.checkWordMatches(2, 'aims', 9, 6, 'aims', my_board)
    # left collision not registering properly: (lose as 'ose' w/o l)


def test_scoring(my_board):
    assert core.Move('otter', (12, 8), my_board, True, score=None).score == 12
    assert core.Move('mem', (9, 9), my_board, True, score=None).score == 7


def test_allMoves(my_letters, my_board):
    newAnswer = algo.allMoves(my_letters, my_board)
    oldAnswer = translatePlay(my_letters, my_board)
    missedSolns = [x for x in oldAnswer if x not in newAnswer]
    newSolns = [x for x in newAnswer if x not in oldAnswer]
    print('\n', my_board, my_letters)
    print(f"missedSolns: {missedSolns}\n newSolns: {newSolns}")
    assert missedSolns == []
    assert newSolns == []


def benchmark():
    gb2 = data.gameBoard = core.load('Oscar2')
    cProfile.runctx("algo.allMoves('asdflet', gb2)", globals(), locals(), sort=1)


def randomPlay():
    gb3 = data.gameBoard = core.Board()
    randomLet = ''.join(np.random.choice(np.array(data.loweralpha), size=7, replace=False))
    player.playMove(randomLet, gb3)

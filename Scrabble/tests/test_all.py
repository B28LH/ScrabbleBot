import pytest
import cProfile
from scrabbler.major import core, data, algo
from scrabbler.oldCodes import scrabblerOLDWRAPPED


def translatePlay(tiles, boardObj):
    result = sorted(scrabblerOLDWRAPPED.BestMove(tiles, boardObj.squares), key=lambda x: x[-1])
    return [core.Move(x[2], x[1], boardObj, score=x[3]) for x in result if x[0] == 2]


@pytest.fixture
def my_board():
    return core.load('ThreeWords')


@pytest.fixture
def my_letters():
    return 'trial'


def test_crossCheck(my_board):
    assert algo.crossChecks(my_board)[5][5] is "INVALID"
    assert algo.crossChecks(my_board)[9][6] is "CLEAR"
    assert algo.crossChecks(my_board)[9][5] is None
    assert isinstance(algo.crossChecks(my_board)[11][5]), type(set())


def test_checkWordMatches(my_board):
    assert algo.checkWordMatches(3, 'amia', 9, 4, 'amia', my_board)
    assert algo.checkWordMatches(2, 'tear', 12, 10, 'tear', my_board)
    assert algo.checkWordMatches(2, 'omen', 8, 10, 'omen', my_board)
    # TODO: BUG TO FIX: (erm)
    # assert algo.checkWordMatches(2, 'erm', 10, 4, 'erm', my_board)
    # Insufficient tiles in rack:
    assert not algo.checkWordMatches(2, 'omen', 8, 10, 'not', my_board)
    # Right collision at end of word
    assert not algo.checkWordMatches(2, 'aims', 9, 6, 'aims', my_board)


def test_scoring(my_board):
    assert core.Move('otter', (12, 8), my_board, score=None).score == 12
    assert core.Move('mem', (9, 9), my_board, score=None).score == 7


def test_botPlay(my_letters, my_board):
    newAnswer = algo.botPlay(my_letters, my_board)
    oldAnswer = translatePlay(my_letters, my_board)
    missedSolns = [x for x in oldAnswer if x not in newAnswer]
    newSolns = [x for x in newAnswer if x not in oldAnswer]
    print('\n', my_board, my_letters)
    print(f"missedSolns: {missedSolns}\n newSolns: {newSolns}")
    assert missedSolns == []
    assert newSolns == []


def benchmark():
    gb2 = data.gameBoard = core.load('Oscar2')
    print(gb2)
    cProfile.run("algo.botPlay('asdflet', gb2)", locals(), sort=1)

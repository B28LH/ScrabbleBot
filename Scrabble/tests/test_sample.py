# Sample Test passing with nose and pytest
import pytest
from scrabbler.major import core, data, algo


@pytest.fixture
def my_board():
    return core.load('ThreeWords')


def test_crossCheck(my_board):
    assert algo.crossChecks(my_board)[5][5] is "INVALID"
    assert algo.crossChecks(my_board)[9][6] is False
    assert algo.crossChecks(my_board)[9][5] is None
    assert type(algo.crossChecks(my_board)[11][5]) == type(set())


def test_checkWordMatches(my_board):
    assert algo.checkWordMatches(2, 'tear', 12, 10, 'tear', my_board)
    assert algo.checkWordMatches(2, 'omen', 8, 10, 'omen', my_board)
    # Insufficient tiles in rack:
    assert not algo.checkWordMatches(2, 'omen', 8, 10, 'not', my_board)
    # Right collision at end of word
    assert not algo.checkWordMatches(2, 'aims', 9, 6, 'aims', my_board)


def test_botPlay(my_board):
    # TODO: create a wrapper for OLDMASTER so that any board and tiles can be compared
    newAnswer = algo.botPlay('me', my_board)
    print(newAnswer)
    oldAnswer = data.testcase
    for item in oldAnswer:
        assert item in newAnswer

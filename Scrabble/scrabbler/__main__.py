from tests import test_all

# TODO:
# Better user input
# Validate / score user input
# Custom difficulty
# Blanks
# Speed analysis
# [''.join(s) for s in substrings('more')]


"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')

To set up:
Find the file data (scrabbler/major/data), change the path variable to where scrabbler file is
"""

test_all.benchmark()
# gb = data.gameBoard = core.Board()
#
# botLet = ''
#
# player.playMove(botLet, gb)
#
# gb = core.load("ThreeWords")
#
# player.playMove('testing', gb)

# gb = data.gameBoard = core.load("ThreeWords")

# Randomplays: tests.randomPlay()

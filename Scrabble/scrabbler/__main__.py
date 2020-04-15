from scrabbler.major import core, data, algo, player
from tests import test_all

# TODO:
# Move first
# Validate / score user input
# Check delete function
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

gb = data.gameBoard = core.Board()
# test_all.benchmark()
#
# botLet = ''
#
# bests = player.playMove(botLet, gb, handicap=0.97)
#
# gb = core.load("ThreeWords")
#
# player.playMove('testing', gb)

# gb = data.gameBoard = core.load("ThreeWords")

# Randomplays:
# tests.randomPlay()

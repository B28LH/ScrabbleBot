from scrabbler.major import core, data, algo, player
from tests import test_all

# TODO:
# Validate / score user input
# Check delete function
# Blanks don't score points
# Speed analysis
# [''.join(s) for s in substrings('more')]


"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')

To set up:
Find the file data (scrabbler/major/data), change the path variable to where scrabbler file is
"""

gb = data.gameBoard = core.Board(design=data.official)
# test_all.benchmark()

#
# gb = core.load("ThreeWords")
#
botLet = 'oRanGes'
bests = player.playMove(botLet, gb)

# # Blank Tiles
# from copy import deepcopy
# tiles = 'qycsne'
# realBests = []
# for char in data.loweralpha:
#     print("Trying: ", char)
#     realBests.extend(algo.allMoves(tiles+char, deepcopy(gb)))
# realBests.sort()

# gb = data.gameBoard = core.load("ThreeWords")

# Randomplays:
# tests.randomPlay()

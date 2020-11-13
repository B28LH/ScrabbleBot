from scrabbler.major import core, data, algo, player
#from tests import test_all

# TODO:
#  Blanks don't score points
#  Speed analysis
#  [''.join(s) for s in substrings('more')]


"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')

To set up:
Find the file data (scrabbler/major/data), change the path variable to where scrabbler file is
"""
# gb = data.gameBoard = core.Board()
player.virtualGame()


# 10.126 seconds

#
# gb = data.gameBoard = core.load("ThreeWords")
#
#
# botLet = 'banana'
# bests = player.playMove(botLet, gb)

# # Blank Tiles
# from copy import deepcopy
# tiles = 'qycsne'
# realBests = []
# for char in data.loweralpha:
#     print("Trying: ", char)
#     realBests.extend(algo.allMoves(tiles+char, deepcopy(gb)))
# realBests.sort()

# Randomplays:
# gb = test_all.randomPlay(gb)

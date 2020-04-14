from scrabbler.major import core, data, algo, player
import numpy as np
from tests import test_all


"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')
"""

gb = data.gameBoard = core.Board(title="Bot2Test1")

# gb = core.load("ThreeWords")
#
# player.playMove('testing', gb)

# gb = data.gameBoard = core.load("ThreeWords")

# test_all.benchmark()

gb.realLayer((3, 7), 'peril', False, display=True)
randomLet = ''.join(np.random.choice(np.array(data.loweralpha), size=7, replace=False))
answers = player.playMove(randomLet, gb)

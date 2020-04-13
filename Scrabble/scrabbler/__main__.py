from scrabbler.major import core, data, algo
from tests import test_all


"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')
"""

gb = data.gameBoard = core.load("ThreeWords")

results = algo.botPlay('test', gb)
print(results)
# test_all.benchmark()

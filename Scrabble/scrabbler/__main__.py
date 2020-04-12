import scrabbler
import dawg
from scrabbler.helpers import core, data, algo
import pickle

# Should this all belong in the __init__.py ???

WWF = False
small = False
title = 'Test5'

"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')
"""

print(data.gameBoard)

a = core.Move('hello', (14, 7), data.gameBoard, score=8)
b = core.Move('bye', (14, 7), data.gameBoard, score=11)
c = core.Move('try', (14, 7), data.gameBoard, score=7)

moves = [a, b, c]
print(moves)
print(sorted(moves))


data.crossed = algo.crossChecks(data.gameBoard)

print(algo.checkWordMatches(1, 'nexus', 11, 6, 'xeus', data.gameBoard))

print(algo.checkWordMatches(4, 'jute', 5, 4, 'random', data.gameBoard))

# algo.botPlay('tryhard',data.gameBoard)

a, b = algo.betterMoveTiles(data.gameBoard, both=True)

from scrabbler.major import core, data, algo
import cProfile
# Should this all belong in the __init__.py ???

WWF = False
small = False
title = 'Test5'

"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')
"""

import cProfile

gb2 = data.gameBoard = core.load('Oscar2')

cProfile.run("algo.botPlay('asdflet', gb2)", sort=1)

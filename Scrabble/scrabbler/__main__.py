import scrabbler
from scrabbler.helpers import core, data, algo
import pickle

WWF = False
small = False
title = 'Test5'

"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')
"""

if scrabbler.WWF:
    data.dictfile = 'wwf.txt'
    data.allTileBonus = 35
    data.startTile = False
    data.tileValues = data.wTileValues
    if scrabbler.small:
        data.design = data.friendsSmall
    else:
        data.design = data.friendsBig
else:
    with open('./Alphabets/collinsdict.pkl', 'rb') as f:
        data.meaningdict = pickle.load(f)

# data.gameBoard = core.Board(title, data.design)
with open(f'./Alphabets/{data.dictfile}', 'r') as infile:
    data.wordset = set(infile.read().split())

data.gameBoard = core.load('Oscar2')

a, b = algo.betterMoveTiles(data.gameBoard, both=True)


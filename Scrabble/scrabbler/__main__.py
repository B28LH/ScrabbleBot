import scrabbler
from scrabbler.helpers import core
from scrabbler.helpers import data
import pickle

"""
TO EXECUTE THE MAIN FILE:
>>> import runpy
>>> runpy.run_module(mod_name='scrabbler')
"""
print("Executing the main")

if scrabbler.WWF:
    data.dictfile = 'wwf.txt'
    data.allTileBonus = 35
    data.startTile = False
    data.tileValues = data.wTileValues
    if scrabbler.Small:
        data.design = data.friendsSmall
    else:
        data.design = data.friendsBig
else:
    with open('./Scrabbler/Alphabets/collinsdict.pkl', 'rb') as f:
        data.meaningdict = pickle.load(f)

# data.gameBoard = core.Board(title, data.design)
with open(f'./Scrabbler/Alphabets/{data.dictfile}', 'r') as infile:
    data.wordset = set(infile.read().split())

data.gameBoard = core.load('Oscar2')
a = core.crossChecks(data.gameBoard)

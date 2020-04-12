from scrabbler.major import core, data, algo
from scrabbler.alphabets import dawgfiler
import pickle
import dawg

WWF = True
small = False
title = 'Sparse'

if WWF:
    data.dictfile = 'wwf'
    data.allTileBonus = 35
    data.startTile = False
    data.tileValues = data.wTileValues
    if small:
        data.design = data.friendsSmall
    else:
        data.design = data.friendsBig
else:
    data.dictfile = 'collins'
    data.allTileBonus = 50
    data.startTile = True
    data.tileValues = data.sTileValues
    data.design = data.official
    with open('./alphabets/collinsdict.pkl', 'rb') as f:
        data.meaningDict = pickle.load(f)

with open(f'./alphabets/{data.dictfile}_set.pkl', 'rb') as infile:
    data.wordset = pickle.load(infile)

data.completor = dawg.CompletionDAWG()
data.completor.load(f'./alphabets/{data.dictfile}.dawg')

gb = data.gameBoard = core.load('Sparse')
# data.gameBoard = core.Board(title, data.design)

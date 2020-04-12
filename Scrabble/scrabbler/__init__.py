import scrabbler
from scrabbler.major import core, data, algo
import pickle
import dawg

WWF = False
small = False
title = 'Sparse'


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
    with open('./alphabets/collinsdict.pkl', 'rb') as f:
        data.meaningdict = pickle.load(f)

# TODO: save the dawgs so they don't have to be constructed every time
with open(f'./alphabets/{data.dictfile}', 'r') as infile:
    data.wordset = set(infile.read().split())

data.dawg = dawg.DAWG(data.wordset)
data.completor = dawg.CompletionDAWG(data.wordset)

gb = data.gameBoard = core.load('Sparse')
# data.gameBoard = core.Board(title, data.design)

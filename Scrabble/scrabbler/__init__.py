import scrabbler
from scrabbler.helpers import core, data, algo
import pickle
import dawg

WWF = False
Small = False
title = 'Test5'


WWF = False
small = False
title = 'Test5'

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

data.dawg = dawg.DAWG(data.wordset)
data.completor = dawg.CompletionDAWG(data.wordset)

data.gameBoard = core.load('Test2')

from helpers import data, core
import pickle

WWF = False
Small = False
title = 'Test5'

if WWF:
    data.dictfile = 'wwf.txt'
    data.allTileBonus = 35
    data.startTile = False
    data.tileValues = data.wTileValues
    if Small:
        data.design = data.friendsSmall
    else:
        data.design = data.friendsBig
else:
    with open(data.path + 'Alphabets/collinsdict.pkl', 'rb') as f:
        data.meaningdict = pickle.load(f)

# data.gameBoard = core.Board(title, data.design)
with open(data.path + f'Alphabets/{data.dictfile}', 'r') as infile:
    data.wordset = set(infile.read().split())

data.gameBoard = core.load('test2')
a = core.crossChecks(data.gameBoard)

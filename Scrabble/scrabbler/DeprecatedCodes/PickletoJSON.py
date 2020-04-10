import pickle
import json
import numpy as np

name = 'Test2'

def DisplayBoard(grid):
    h = range(len(grid))
    if len(grid) < 10:
        print('    ' + '|'.join(map(str, h)))
    else:
        print('    ' + '|'.join([x[0] if int(x) > 9 else ' ' for x in map(str, h)]))
        print('    ' + '|'.join([x[1] if int(x) > 9 else x for x in map(str, h)]))
    for i, x in enumerate(grid):
        if i < 10: i = str(i) + ' '
        print(i, '|' + ' '.join(x))


def LoadGame(Name):
    with open('ScrabbleGames/%s.pkl' % Name, 'rb') as f:
        GameBoard = pickle.load(f)
    print("Game '%s' loaded" % Name)
    DisplayBoard(GameBoard)
    return GameBoard

a = LoadGame(name)


def SaveJSON(Name, Game):
    with open('ScrabbleGames/{}.json'.format(Name), 'w', encoding='utf-8') as outFile:
        json.dump(Game,outFile, ensure_ascii=False, indent=4)

SaveJSON(name,a.tolist())

def ReadJSON(Name):
    with open('ScrabbleGames/{}.json'.format(Name), 'r') as inFile:
        a = np.array(json.load(inFile))
    print(a)
    DisplayBoard(a)

ReadJSON(name)

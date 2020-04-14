from scrabbler.major import core, data, algo


def isWord(word):
    return word in data.wordset


def meaning(word):
    assert isWord(word), "Not a word"
    return data.meaningDict[word]


def playMove(rack, boardObj):
    theMoves = algo.allMoves(rack, boardObj)
    print(boardObj)
    if len(theMoves) > 0:
        myMove = theMoves[-1]  # TODO: Implement difficulty levels
        print(f"\nI play {myMove}:")
        boardObj.layerMoveObj(myMove)
        print(meaning(myMove.word))
    else:
        print("I cannot play a move :(")


def castMove(moveStr, boardObj=data.gameBoard):
    direction, row, col, word = moveStr.split()
    moveObj = core.Move(word, (row, col), boardObj, across=(direction == 'a'))
    boardObj.layer(moveObj)

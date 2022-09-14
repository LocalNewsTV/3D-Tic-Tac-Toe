#!/usr/bin/python3
###########################################################################
# @returns {Array} Array representing a 4x4x4 game board 
###########################################################################
def setUpBoard():
    return [[['_']*4]*4]*4
###########################################################################
# @returns {string} easily readable stringified version of our game board array
###########################################################################
def displayBoard():
    boardString = ''
    for x in board:
        for y in x:
            boardString += (" ").join(y) + '\n'
        boardString += '\n'
    boardString += '\n'
    return boardString

board = setUpBoard()
print(displayBoard())
print(":)")
print(board[0])
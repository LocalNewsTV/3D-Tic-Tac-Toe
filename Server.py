#!/usr/bin/python3
from selectors import EpollSelector
import socket
import re
BUF_SIZE = 1024
HOST = ''
PORT = 12345

COMMAND = 0
LAYER = 1
ROW = 2
COLUMN = 3
TOKEN = 4
TOKEN_START = 1
TOKEN_MAX = 3
MATCH_ONCE_ONLY = 1

###########################################################################
# @desc - Sets up a blank gameboard to play with
# @returns {Array} - Array representing a 4x4x4 game board 
###########################################################################
def setUpBoard():
    GRID_SIZE = 4
    return [[['_' for _ in range(GRID_SIZE)]for _ in range(GRID_SIZE) ] for _ in range(GRID_SIZE) ] 

###########################################################################
# @description - Stringifies the gameBoard to be returned by the TCP server
# @param gameBoard {Array} - Current gameboard in play
# @returns {String} - Easily readable stringified version of our gameBoard array
###########################################################################
def displayBoard(gameBoard):
    boardString = ''
    for x in gameBoard:
        for y in x:
            for z in y:
                boardString += str(z)
            boardString += '\n'
        boardString += '\n'
    boardString += '\n'
    return boardString

###########################################################################
# @desc - Compares users token to the current Token. if valid, makes move.
# @param requestArray {Array} - Users move input, put into an array
# @param gameBoard {Array} - current gameBoard in use
# @param currentToken {integer} - valid turn token for the game
# @returns {String} - [E]rror or [O]K for TCP servers response
###########################################################################
def usersMove(requestArray, gameBoard, currentToken):
    if (requestArray[TOKEN] == currentToken):
        if makePlayerMove(requestArray, gameBoard):
            return 'O\n'
    return "E\n"

###########################################################################
# @desc - Checks the space selected by user for "_", then places Token
# @param rA {Array} - Input from user. "requestArray" shortened
# @param gameBoard {Array} - current gameBoard in use
# @returns {boolean} - turn successful
###########################################################################
def makePlayerMove(rA, gameBoard):
    if gameBoard[rA[LAYER]][rA[ROW]][rA[COLUMN]] == '_':
        gameBoard[rA[LAYER]][rA[ROW]][rA[COLUMN]] = rA[TOKEN]
        return True
    else:
        return False
###########################################################################
# @desc - Checks current value of token and resets if necessary
# @param currentToken {integer} - current value of token when turn was made
# @returns {integer} - updated Token value
###########################################################################
def updateToken(currentToken):
    currentToken += 1
    if currentToken > TOKEN_MAX:
        currentToken = TOKEN_START
    return currentToken

###########################################################################
# @desc - Main controller for the TCP server game. constantly listens for an input
#   and acts accordingly. sends an encoded string as a response and 
#   severs the connection. runs indefinitely 
#   User inputs should be: 
#       "G" - GET
#       "P" - PUT
#       "C" - CLEAR
#   Server should respond with:
#        A Stringified Board
#       "O" - OK
#       "E" - ERROR
###########################################################################
def boardGame():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # TCP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT)) # Claim messages sent to port "PORT"
        sock.listen(1) # Enable server to receive 1 connection at a time
        print('Server:', sock.getsockname()) # Source IP and port
        gameBoard = setUpBoard()
        serverResponse = ''
        currentToken = TOKEN_START
        while True:
            sc, sockname = sock.accept() # Wait until a connection is established
            
            with sc:
                print('Client:', sc.getpeername()) # Dest. IP and port
                data = sc.recv(BUF_SIZE) # recvfrom not needed since address is known
                userRequest = data.decode().strip().upper()
                userRequestMove = len(re.findall('^P[0-3][0-3][0-3][0-3]$', userRequest)) == MATCH_ONCE_ONLY
                
                if(userRequest == 'G'):
                    serverResponse = displayBoard(gameBoard)
                elif userRequestMove:
                    requestArray = [int(userRequest[LAYER]), int(userRequest[ROW]), int(userRequest[COLUMN]), int(userRequest[TOKEN])]
                    serverResponse = usersMove(requestArray, gameBoard, currentToken)
                    if userRequest[COMMAND] == 'O':
                        currentToken = updateToken(currentToken)
                elif userRequest == 'C':
                    gameBoard = setUpBoard()
                    currentToken = TOKEN_START
                    serverResponse = 'O\n'
                else:
                    serverResponse = 'E\n'
                    
                sc.sendall(serverResponse.encode('utf-8')) # Dest. IP and port implicit due to accept call

boardGame()
#!/usr/bin/python3
from selectors import EpollSelector
import socket
import re
BUF_SIZE = 1024
HOST = ''
PORT = 12345

###########################################################################
# @returns {Array} Array representing a 4x4x4 game board 
###########################################################################
def setUpBoard():
    return [[['_' for _ in range(4)]for _ in range(4) ] for _ in range(4) ] 
###########################################################################
# @returns {string} easily readable stringified version of our game board array
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

def makeTurn(num, gameBoard):
    gameBoard[int(num[1])][int(num[2])][int(num[3])] = int(num[4])

def validateTurn(num, gameBoard):
    print(num)
    if gameBoard[int(num[1])][int(num[2])][int(num[3])] == '_':
        makeTurn(num, gameBoard)
        return True
    else:
        return False
def usersMove(userRequest, gameBoard, currentToken):
    validToken = (int(userRequest[4]) == currentToken)
    if validToken:
        validTurn = validateTurn(userRequest, gameBoard)
        if validTurn:
            return 'O\n'
        return "E\n" #delete later
    return "E\n"
def updateToken(currentToken):
    currentToken += 1
    if currentToken > 3:
        currentToken = 1
    return currentToken
def boardGame():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # TCP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Details later
        sock.bind((HOST, PORT)) # Claim messages sent to port "PORT"
        sock.listen(1) # Enable server to receive 1 connection at a time
        print('Server:', sock.getsockname()) # Source IP and port
        gameBoard = setUpBoard()
        serverResponse = ''
        currentToken = 1
        
        while True:
            sc, sockname = sock.accept() # Wait until a connection is established
            
            with sc:
                print('Client:', sc.getpeername()) # Dest. IP and port
                data = sc.recv(BUF_SIZE) # recvfrom not needed since address is known
                userRequest = data.decode().strip().upper()
                userRequestMove = len(re.findall('^P[0-3][0-3][0-3][0-3]$', userRequest)) == 1
                
                if(userRequest == 'G'):
                    serverResponse = displayBoard(gameBoard)
                elif userRequestMove:
                    serverResponse = usersMove(userRequest, gameBoard, currentToken)
                    if serverResponse[0] == 'O':
                        currentToken = updateToken(currentToken)
                elif userRequest == 'C':
                    gameBoard = setUpBoard()
                    currentToken = 1
                    serverResponse = 'O\n'
                elif userRequest == 'CT':
                    serverResponse = str(currentToken) + '\n'
                else:
                    serverResponse = 'E\n'
                sc.sendall(serverResponse.encode('utf-8')) # Dest. IP and port implicit due to accept call

boardGame()
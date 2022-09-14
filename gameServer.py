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
                boardString += str(z) + ' '
            boardString += '\n'
        boardString += '\n'
    boardString += '\n'
    return boardString

def makeTurn(num):
    gameBoard[int(num[1]) - 1][int(num[2]) - 1][int(num[3]) - 1] = int(num[4])

def validateTurn(pick):
    num = list(pick)
    print(num)
    if gameBoard[int(num[1]) - 1][int(num[2]) - 1][int(num[3]) - 1] == '_':
        makeTurn(num)
        return ''
    else:
        return 'ERROR \n'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # TCP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Details later
    sock.bind((HOST, PORT)) # Claim messages sent to port "PORT"
    sock.listen(1) # Enable server to receive 1 connection at a time
    print('Server:', sock.getsockname()) # Source IP and port
    gameBoard = setUpBoard()
    returnData = ''
    while True:
        sc, sockname = sock.accept() # Wait until a connection is established
        with sc:
            print('Client:', sc.getpeername()) # Dest. IP and port
            data = sc.recv(BUF_SIZE) # recvfrom not needed since address is known
            userRequest = data.decode().strip().lower()
            print(userRequest)
            if(userRequest[0] == 'g'):
                print(displayBoard(gameBoard))
                returnData = displayBoard(gameBoard)
            elif len(re.findall('^p[1-4][1-4][1-4][0-9]$', userRequest)) == 1:
                returnData = validateTurn(userRequest)
            else:
                returnData = 'ERROR\n'
            sc.sendall(returnData.encode('utf-8')) # Dest. IP and port implicit due to accept call

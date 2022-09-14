#!/usr/bin/python3
import socket
BUF_SIZE = 1024
HOST = ''
PORT = 12345

###########################################################################
# @returns {Array} Array representing a 4x4x4 game board 
###########################################################################
def setUpBoard():
    return [[['_']*4]*4]*4
###########################################################################
# @returns {string} easily readable stringified version of our game board array
###########################################################################
def displayBoard(gameBoard):
    boardString = ''
    for x in gameBoard:
        for y in x:
            boardString += (" ").join(y) + '\n'
        boardString += '\n'
    boardString += '\n'
    return boardString

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
            userRequest = data.decode()
            print(userRequest)
            if(userRequest.lower() == 'g'):
                print(displayBoard(gameBoard))
                returnData = displayBoard(gameBoard)
            print(returnData)
            sc.sendall(returnData.encode('utf-8')) # Dest. IP and port implicit due to accept call
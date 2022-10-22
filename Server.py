#!/usr/bin/python3
#############################################################################
#    Author: Matthew Logan
#    Student Number: C0404259
#    Class: ICS226, Fall 2022
#    Description: Server for 3D Tic Tac Toe
#############################################################################
import gameBoard as game
import traceback, logging, logging.handlers, threading, socket, time
BUF_SIZE = 1
HOST = ''
PORT = 12345
TOKEN_START = 1
MAX_PLAYERS = 3
LAST = -1
FIRST = 0
PLAY_TOKEN = 4

################################################################################################################
# @desc - Controller for each player. Takes input until '*' is received, signalling termination of reply
#         Server removes * from command and send data to game instance. the server is responsible for:
#               -Validating the players token matches their id
#               -Enforcing turn order with semaphores so players moves are kept in order
#               -Setting turn order back to player 1 if the board is cleared
#               -Logging data to journalctl
#               -responding to all user requests
# @param(id) {int} - int representing ID of player
# @param(sc) {Object} - reference to the players Socket connection, for communication
# @param(game) {Object} - reference to the GameBoard object, so user can play
# @param(logger) {Object} - Reference to the logger Object, for journaling
# @param(locks) {Array} - Reference to the locks array, a collection of semaphores
#
################################################################################################################
def calledByThread(id, sc, game, logger, locks):
    response = ""
    with sc:
        try:
            while True:
                dataList = ""
                while (len(dataList) == 0 or dataList[LAST] != '*'):
                    dataList += sc.recv(BUF_SIZE).decode().strip().upper()
                dataList = list(dataList)

                logger.debug("User sent:" + str(dataList))
                dataList.pop()
                logger.debug("Valid command")
                if(dataList[FIRST] == "P" and str(id) == dataList[PLAY_TOKEN]):
                    if (game.checkPositionAvailable(dataList) and game.checkWhoseTurn() == id):
                        logger.debug("P - Locking Player, making move")
                        locks[id -1].acquire()
                        response = game.gamePlay(id, dataList)
                        logger.debug("Releasing player" + str(id % MAX_PLAYERS))
                        locks[id % MAX_PLAYERS].release()
                    else:
                        logger.debug("P - was invalid")
                        response = 'E'
                elif(dataList[FIRST] == 'C'):
                    logger.debug("Player " + str(id) + ": Clearing Board")
                    locks[FIRST].release()
                    response = game.gamePlay(id, dataList)
                else:
                    response = game.gamePlay(id, dataList)
                sc.sendall((response + '*').encode('utf-8')) # Dest. IP and port implicit due to accept call

        except Exception as details:
            logger.debug(details)


######################################################################################################################################################
# @desc - Main controller for the TCP server game. Responsible for:
#           -Setting up threads/semaphores for players equal to {MAX_PLAYERS}
#           -Creating and passing instance of GameBoard
#           -Rejecting all connections that exceed MAX_PLAYERS
#           -Logging data to journalctl
#           -Opening turns to the first player when all players have joined 
######################################################################################################################################################
def startGame():
    currentToken = TOKEN_START
    userConnections = []
    locks = []
    
    logger = logging.getLogger('client.py')
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    logger.addHandler(handler)

    gameInstance = game.GameBoard(MAX_PLAYERS)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # TCP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT)) # Claim messages sent to port "PORT"
        sock.listen(1) # Enable server to receive 1 connection at a time
        logger.debug('Server:' + str(sock.getsockname())) # Source IP and port
        while True:
            try:
                sc, sockname = sock.accept() # Wait until a connection is established
                if(currentToken <= MAX_PLAYERS):
                    logger.debug('Player connected')
                    locks.append(threading.Semaphore())
                    locks[LAST].acquire()
                    threading.Thread(target = calledByThread, args = (currentToken, sc, gameInstance, logger, locks)).start()
                    userConnections.append(sc)
                    currentToken += 1
                    if(currentToken > MAX_PLAYERS):
                        locks[FIRST].release()
                else:
                    logger.debug('Rejected Connection')
                    sc.sendall("R*".encode('utf-8'))
                    sc.close()

            except Exception as details:
                logger.debug(details)

startGame()

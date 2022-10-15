#!/usr/bin/python3
import gameBoard as game
import traceback, logging, logging.handlers, threading, socket, time
BUF_SIZE = 1024
HOST = ''
PORT = 12345
TOKEN_START = 1
MAX_PLAYERS = 3
LAST = -1
FIRST = 0


def calledByThread(id, sc, game, logger, locks):
    response = ""
    with sc:
        try:
            while True:
                dataList = list(sc.recv(BUF_SIZE).decode().strip().upper())
                logger.debug(dataList)
                if(dataList[LAST] == "*"):
                    logger.debug("Valid command")
                    if(dataList[FIRST] == "P"):
                        if (id == game.getToken()):
                            response = game.gamePlay(int(id), dataList)
                            if response != 'E':
                                locks[id -1].acquire()
                                locks[id % MAX_PLAYERS].release()
                        else:
                            response = 'E'
                    elif(dataList[FIRST] == 'C'):
                        locks[0].release()
                        response = game.gamePlay(int(id), dataList)
                    else:
                        response = game.gamePlay(int(id), dataList)
                else:
                    logger.debug("Bad command")
                    response = 'E'
                logger.debug("Response>" + response)
                sc.sendall((response + '*').encode('utf-8')) # Dest. IP and port implicit due to accept call
        except Exception as details:
            traceback.print_exc()
            sc.close()


###########################################################################
# @desc - Main controller for the TCP server game. constantly listens for an input
#   and acts accordingly. sends an encoded string as a response and 
#   severs the connection. runs indefinitely 
###########################################################################
def startGame():
    currentToken = TOKEN_START
    userConnections = []
    locks = []
    
    logger = logging.getLogger('client.py')
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    logger.addHandler(handler)

    gameInstance = game.GameBoard(MAX_PLAYERS, logger)
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
                    if(currentToken > 3):
                        locks[0].release()
                else:
                    logger.debug('Rejected Connection')
                    sc.sendall("R*".encode('utf-8'))
                    sc.close()

            except Exception as details:
                logger.debug(details)

startGame()

#!/usr/bin/python3
#############################################################################
#    Author: Matthew Logan
#    Student Number: C0404259
#    Class: ICS226, Fall 2022
#    Description: Server for 3D Tic Tac Toe
#############################################################################
import gameBoard as game
import traceback, logging, logging.handlers, asyncio
HOST = ''
PORT = 12345
MAX_PLAYERS = 3

#############################################################################
#   @desc - Class made for the server side of TTT, runs with Asyncio to maintain
#           players based on their session ids. Member functions in this class
#           allow us to keep track of players turns 
#############################################################################
class ClientHandler:
    FIRST = 0
    LAST = -1
    def __init__(self, TTT):
        self._MAX_PLAYERS = MAX_PLAYERS
        self._players = []
        self._gameBoard = TTT
        self._logger = self.initLogger()
        self._currentPlayers = 0

    #############################################################################
    # @desc - creates and returns a logger object
    #############################################################################
    def initLogger(self):
        logger = logging.getLogger('client.py')
        logger.setLevel(logging.DEBUG)
        handler = logging.handlers.SysLogHandler(address = '/dev/log')
        logger.addHandler(handler)
        return logger

    #############################################################################
    # @desc - Appends a players session ID to the players array and creates
    #         game ID
    # @param id {Integer} - Session ID 
    # @returns - Players Token ID for the game session
    #############################################################################
    def addPlayer(self, sessionID):
        self._players.append(sessionID)
        return self._players.index(sessionID) + 1
    #############################################################################
    # @desc - Returns number of players in game Instance
    #############################################################################
    def getPlayerCount(self):
        return self._currentPlayers
        
    #############################################################################
    # @desc - Increments player count when player has joined
    #############################################################################
    def incrementPlayerCount(self):
        self._currentPlayers += 1

    #############################################################################
    # @desc - Handler for all player connections           
    #############################################################################
    async def handle_player(self, reader, writer):
        try:
            if(self.getPlayerCount() < self._MAX_PLAYERS):
                self.incrementPlayerCount()
                id = writer.get_extra_info('peername')
                id = self.addPlayer(id[1])
                
                while True:
                    response = ""
                    userInput = await reader.readuntil(separator=b'*')
                    userInput = userInput.decode().strip().upper()
                    userInput = list(userInput)
                    self._logger.debug("User sent:" + str(userInput))
                    userInput.pop()
                    self._logger.debug("Player ", id, "made turn.")

                    if(userInput[self.FIRST] == "P"):
                        if (GAME_INSTANCE.checkPositionAvailable(userInput)):
                            response = GAME_INSTANCE.gamePlay(id, userInput)
                        else:
                            self._logger.debug("P - was invalid")
                            response = 'E'
                    else:
                        response = GAME_INSTANCE.gamePlay(id, userInput)
                    
                    response = (response + '*').encode('utf-8')
                    writer.write(response)
                    await writer.drain()
            else:
                response = "R*".encode('utf-8')
                writer.write(response)
                await writer.drain()
                writer.close()
                self._logger.debug("Rejected connection")
        except Exception as details:
            traceback.print_exc
            self._logger.debug(details)



#############################################################################
# @desc - main method for the TicTacToe Server, responsible for taking in player
#         connections and handing them off to the handler class
#         Initializes both clientHandler and GameBoard objects
#############################################################################
async def main():
        global GAME_INSTANCE
        GAME_INSTANCE = game.GameBoard(MAX_PLAYERS)
        handler = ClientHandler(GAME_INSTANCE)
        server = await asyncio.start_server(handler.handle_player, HOST, PORT)
        await server.serve_forever()
        traceback.print_exc

asyncio.run(main())

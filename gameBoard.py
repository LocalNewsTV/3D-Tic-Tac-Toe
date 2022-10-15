import re

class GameBoard:
    COMMAND = 0
    TOKEN_START = 1
    MATCH_ONCE_ONLY = 1
    GRID_SIZE = 4
    ID = 4
    
    def __init__(self, NUM_PLAYERS, logger):
        self._NUM_PLAYERS = NUM_PLAYERS
        self._TOKEN_MAX = NUM_PLAYERS
        self._board = self.setUpBoard()
        self._currentTurn = 1
        self._command = []
        self._winner = False
        self._winnerID = None
        self._logger = logger
    ###########################################################################
    # @description - Stringifies the gameBoard to be returned by the TCP server
    # @returns {String} - Easily readable stringified version of our gameBoard array
    ###########################################################################
    def displayGameBoard(self):
        boardString = ""
        for x in self._board:
            for y in x:
                for z in y:
                    boardString += str(z)
                boardString += '\n'
            boardString += '\n'
        if self._winner:
            boardString += 'Player ' + str(self._winnerID) + ' wins'
        else:    
            boardString += 'Player ' + str(self._currentTurn) + "'s turn"
        return boardString

    ###########################################################################
    # @desc - Sets up a blank gameboard to play with
    # @returns {Array} - 3D Array representing a 4x4x4 game board 
    ###########################################################################
    def setUpBoard(self):
        return [[['_' for _ in range(self.GRID_SIZE)]for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE) ] 


    ###########################################################################
    # @desc - Checks current value of token and resets if necessary
    # @returns {integer} - updated Token value
    ###########################################################################
    def updateTurn(self):
        self._currentTurn += 1
        if self._currentTurn > self._TOKEN_MAX:
            self._currentTurn = self.TOKEN_START 

    ##########################################################################
    #
    #
    ###########################################################################
    def newGame(self):
        self._board = self.setUpBoard()
        self._currentTurn = self.TOKEN_START
        self._winner = False
        self._winnerID = None
    ###########################################################################
    # @desc - Checks the space selected by user for "_", then places Token
    # @param rA {Array} - Input from user. "requestArray" shortened
    # @param gameBoard {Array} - current gameBoard in use
    # @returns {boolean} - turn successful
    ###########################################################################
    def makePlayerMove(self):
        layer, row, column, token = self._command 
        if self._board[layer][row][column] == '_':
            self._board[layer][row][column] = token
            return True
        else:
            return False


    def checkPositionAvailable(self, data):
        turn = data.copy()
        turn.pop()
        userRequestedTurn = len(re.findall('^P[0-3][0-3][0-3][0-3]$', ('').join(turn))) == self.MATCH_ONCE_ONLY
        turn.pop(0)
        layer, row, column, token = turn 
        if(userRequestedTurn):
            return self._board[int(layer)][int(row)][int(column)] == '_'
        else:
            return False
    ###########################################################################
    #
    #
    ###########################################################################
    def gamePlay(self, id, userTurn):
        if(len(userTurn) > 1):
            userTurn.pop()
        else:
            return 'O'
        userRequestedTurn = len(re.findall('^P[0-3][0-3][0-3][0-3]$', ('').join(userTurn))) == self.MATCH_ONCE_ONLY

        if (userRequestedTurn and self._currentTurn == id and int(userTurn[self.ID]) == id):
            self._command = [int(userTurn[1]),int(userTurn[2]),int(userTurn[3]), int(userTurn[4])]
            if (self._winner == False and self.makePlayerMove()):
                self.updateTurn()
                self.checkForWins()
                return 'O'
            return 'E'

        elif (userTurn[self.COMMAND] == 'G'):
            return self.displayGameBoard()

        elif (userTurn[self.COMMAND] == 'C'):
            self.newGame()
            return 'O'

        else:
            return 'E'

    ###########################################################################
    # desc - Checks for Win conditions going horizontally, either on a single plane
    #        or across the boards. Also if a win goes straight down
    # returns - {boolean} if a win condition was met horizontally
    ###########################################################################
    def winHorizontal(self,):
        test = [True, True, True, True]
        layer, row, column, token = self._command

        for data in self._board[layer][row]:
            if(data != token):
                test[0] = False

        if not test[0]:
            for i in range(self.GRID_SIZE):
                if(self._board[i][row][i] != token):
                    test[1] = False

            if not test[1]:
                j = 0
                for i in range(self.GRID_SIZE -1, -1, -1):
                    if(self._board[i][row][j] != token):
                        test[2] = False
                    j += 1   

                if not test[2]:
                    for i in range(self.GRID_SIZE):
                        if(self._board[i][row][column] != token):
                            test[3] = False  
                    
        return True in test

    ###########################################################################
    # desc - Checks for Win conditions going vertically, either on a single plane
    #        or across the boards
    # returns - {boolean} if a win condition was met vertically
    ###########################################################################
    def winVertical(self):
        test = [True, True, True]
        layer, row, column, token = self._command

        for i in range(self.GRID_SIZE):
            if(self._board[layer][i][column] != token):
                test[0] = False

        if not test[0]:
            for i in range(self.GRID_SIZE):
                if(self._board[i][i][column] != token):
                    test[1] = False
            
            if not test[1]:
                j = 0
                for i in range(self.GRID_SIZE -1, -1, -1):
                    if(self._board[i][j][column] != token):
                        test[2] = False
                    j += 1     

        return True in test     
                
    ###########################################################################
    # TODO:
    # """desc - Checks for Win conditions going Diagonally, either on a single plane
    #        or across the boards
    # returns - {boolean} if a win condition was met vertically"""
    ###########################################################################
    def winDiagonal(self):
        for tables in self._board:
            for rows in tables:
                for columns in rows:
                    return False

    ###########################################################################
    # @desc - 
    #
    ###########################################################################
    def checkForWins(self):
        test = [self.winDiagonal(), self.winHorizontal(), self.winVertical()]
        self._logger.debug(test)
        if True in test:
            self._winner = True
            self._winnerID = self._command[self.ID -1]
            

    def checkWhoseTurn(self):
        return self._currentTurn
#!/usr/bin/python3

#############################################################################
#    Author: Matthew Logan
#    Student Number: C0404259
#    Class: ICS226, Fall 2022
#    Description: Class Object for game of 3D Tic Tac Toe using 4x4x4 grid
#    Parameters: NUM_PLAYERS {integer} - Number of players in this session
#############################################################################
import re
class GameBoard:
    _COMMAND = 0
    _TOKEN_START = 1
    _MATCH_ONCE_ONLY = 1
    _GRID_SIZE = 4
    _ID = 4
    PLAY = 'P'
    CLEAR = 'C'
    GET = 'G'
    OK = 'O'
    ERROR = 'E'
    EMPTY = '_'
    _PLAY_REGEX = '^P[0-3][0-3][0-3][0-3]$'
    
    def __init__(self, NUM_PLAYERS,):
        self._TOKEN_MAX = NUM_PLAYERS
        self._board = self._setUpBoard()
        self._currentTurn = 1
        self._playerInput = []
        self._isWinner = False
        self._winnerID = None
        self._turnsTaken = 0
        self._MINIMUM_TURNS_TO_WIN = (NUM_PLAYERS * 3) + 1

    ###########################################################################
    # @description - Creates a stringified copy of the game board
    # @returns {String} - readable stringified version of our gameBoard
    ###########################################################################
    def _displayGameBoard(self):
        boardString = ""
        for layers in self._board:
            for rows in layers:
                for column in rows:
                    boardString += str(column)
                boardString += '\n'
            boardString += '\n'
        if self._isWinner:
            boardString += 'Player ' + str(self._winnerID) + ' wins'
        else:    
            boardString += 'Player ' + str(self._currentTurn) + "'s turn"
        return boardString

    ###########################################################################
    # @desc - creates an empty gameBoard array
    # @returns {Array} - 3D Array representing a 4x4x4 game board 
    ###########################################################################
    def _setUpBoard(self):
        return [[['_' for _ in range(self._GRID_SIZE)]for _ in range(self._GRID_SIZE)] for _ in range(self._GRID_SIZE) ] 

    ##########################################################################
    # @desc - Sets up board for a new game to be played
    ###########################################################################
    def _newGame(self):
        self._board = self._setUpBoard()
        self._currentTurn = self._TOKEN_START
        self._isWinner = False
        self._winnerID = None
        self._turnsTaken = 0


    ###########################################################################
    # @desc - Returns ID of player that will play next
    ###########################################################################
    def checkWhoseTurn(self):
        return self._currentTurn

    ###########################################################################
    # @desc - adjusts integer for keeping track of player turn
    ###########################################################################
    def _updateTurn(self):
        self._currentTurn += 1
        if self._currentTurn > self._TOKEN_MAX:
            self._currentTurn = self._TOKEN_START 

    ###########################################################################
    # @desc - Checks the space selected by user for "_", then places Token
    # @returns {boolean} - turn successful
    ###########################################################################
    def _makePlayerMove(self):
        layer, row, column, token = self._playerInput 
        if self._board[layer][row][column] == self.EMPTY:
            self._board[layer][row][column] = token
            return True
        else:
            return False

    ###########################################################################
    # @desc - Method for server to directly call, confirms that player is 
    #         requesting a valid move, before semaphores are adjusted
    # @returns {boolean} - the specified space on the board is available
    ###########################################################################
    def checkPositionAvailable(self, data):
        userRequestedTurn = len(re.findall(self._PLAY_REGEX, ('').join(data))) == self._MATCH_ONCE_ONLY
        if(userRequestedTurn):
            turn = data.copy()
            turn.pop(0)
            turn = list(map(int, turn))
            layer, row, column, token = turn 
            return self._board[layer][row][column] == self.EMPTY
        else:
            return False

    ###########################################################################
    # @desc - Checks all win conditions that go horizontally on board across 1-4 layers
    #         uses shortcircuiting to reduce time complexity
    # @return - {boolean} if a win condition was met horizontally
    ###########################################################################
    def _testHorizontalWin(self,):
        layer, row, column, token = self._playerInput
        def test1():    
            #In single layer
            for data in self._board[layer][row]:
                if(data != token):
                    return False
            return True
        def test2():
            #from Top Layer to Bottom Layer
            for i in range(self._GRID_SIZE):
                if(self._board[i][row][i] != token):
                    return False
            return True
        def test3():
            #From Bottom Layer to Top Layer
            j = self._GRID_SIZE -1
            for i in range(self._GRID_SIZE):
                if(self._board[i][row][j] != token):
                    return False
                j -= 1   
            return True
        def test4():
            #straight downward across layers
            for i in range(self._GRID_SIZE):
                if(self._board[i][row][column] != token):
                    return False  
            return True
        return test1() or test2() or test3() or test4()

    ###########################################################################
    # @desc - Test for any form of Vertical win across 1-4 boards, 
    #         Uses short circuiting to reduce time complexity of tests
    # @return - {boolean} if a win condition was met vertically
    ###########################################################################
    def _testVerticalWin(self):
        layer, row, column, token = self._playerInput
        def test1():
            #in one layer
            for i in range(self._GRID_SIZE):
                if(self._board[layer][i][column] != token):
                    return False
            return True
        def test2():
            #between layers starting from top
            for i in range(self._GRID_SIZE):
                if(self._board[i][i][column] != token):
                    return False
            return True
        def test3():
            #between layers starting from bottom
            j = self._GRID_SIZE - 1
            for i in range(self._GRID_SIZE):
                if(self._board[j][i][column] != token):
                    return False
                j -= 1     
            return True

        return test1() or test2() or test3()     
                
    ###########################################################################
    # @desc - Checks for Win conditions going Diagonally, either on a single plane
    #         or across the boards. Uses Shortcircuiting for time complexity
    # @return - {boolean} if a win condition was met vertically on any plane
    ###########################################################################
    def _testDiagonalWin(self):
        layer, row, column, token = self._playerInput
        def test1():
            #Left to right across all boards    
            for i in range(self._GRID_SIZE):
                if self._board[i][i][i] != token:
                    return False
            return True
        def test2():
            #Right to left across all boards
            j = self._GRID_SIZE - 1
            for i in range(self._GRID_SIZE):
                if(self._board[i][i][j] != token):
                    return False
                j -= 1
            return True
        def test3():
            #Left to right, single layer
            for i in range(self._GRID_SIZE):
                if(self._board[layer][i][i] != token):
                    return False
            return True
        def test4():
            #Right to left single layer
            j = self._GRID_SIZE - 1 
            for i in range(self._GRID_SIZE):
                if(self._board[layer][i][j] != token):
                    return False
                j -= 1
            return True
        def test5():
            #Bottom left to Top right across layers
            j = self._GRID_SIZE -1
            for i in range(self._GRID_SIZE):
                if(self._board[i][j][i] != token):
                    return False
                j -= 1
            return True
        def test6():
            #Bottom Right to Top Left across layers
            j = self._GRID_SIZE -1
            for i in range(self._GRID_SIZE):
                if(self._board[i][j][j] != token):
                    return False
                j -= 1
            return True

        return test1() or test2() or test3() or test4() or test5() or test6()

    ###########################################################################
    # @desc - Runs all checks for a game win. Only checks after minimum number
    #         of turns has been played to reduce needless checking
    ###########################################################################
    def _checkForWins(self):
        self._turnsTaken += 1
        if self._turnsTaken >= self._MINIMUM_TURNS_TO_WIN:
            if self._testDiagonalWin() or self._testHorizontalWin() or self._testVerticalWin():
                self._isWinner = True
                self._winnerID = self._playerInput[self._ID -1]
            
    ###########################################################################
    # @desc - Main turn control for the TTT Board. Handles:
    #               "P" - Handling Players Turns      
    #               "C" - Resetting the Game
    #               "G" - Sending a readable copy of the Board
    # @param id {Integer} - ID of the player submitting a turn
    # @param userTurn {Array} - Command received by player, formatted as an array
    ###########################################################################
    def gamePlay(self, id, userTurn):
        userRequestedTurn = len(re.findall(self._PLAY_REGEX, ('').join(userTurn))) == self._MATCH_ONCE_ONLY
        
        if (userRequestedTurn and self._currentTurn == id and int(userTurn[self._ID]) == id):
            userTurn.pop(0) #Remove the P from {userTurn}
            self._playerInput = list(map(int, userTurn))
            if (not self._isWinner and self._makePlayerMove()):
                self._updateTurn()
                self._checkForWins()
                return self.OK
            return self.ERROR

        elif (userTurn[self._COMMAND] == self.GET):
            return self._displayGameBoard()
            
        elif (userTurn[self._COMMAND] == self.CLEAR):
            self._newGame()
            return self.OK
        else:
            return self.ERROR

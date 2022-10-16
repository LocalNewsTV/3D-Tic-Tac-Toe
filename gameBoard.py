#!/usr/bin/python3
#############################################################################
#    Author: Matthew Logan
#    Student Number: C0404259
#    Class: ICS226, Fall 2022
#    Description: Class Object for game of 3D Tic Tac Toe using 4x4x4 grid
#############################################################################
import re
class GameBoard:
    COMMAND = 0
    TOKEN_START = 1
    MATCH_ONCE_ONLY = 1
    GRID_SIZE = 4
    ID = 4
    MINIMUM_TURNS_TO_WIN = 10
    
    def __init__(self, NUM_PLAYERS,):
        self._NUM_PLAYERS = NUM_PLAYERS
        self._TOKEN_MAX = NUM_PLAYERS
        self._board = self.setUpBoard()
        self._currentTurn = 1
        self._command = []
        self._winner = False
        self._winnerID = None
        self._turnsTaken = 0

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
    # @desc - Sets up board for a new game to be played 
    ###########################################################################
    def newGame(self):
        self._board = self.setUpBoard()
        self._currentTurn = self.TOKEN_START
        self._winner = False
        self._winnerID = None
        self._turnsTaken = 0
    ###########################################################################
    # @desc - Checks the space selected by user for "_", then places Token
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
        userRequestedTurn = len(re.findall('^P[0-3][0-3][0-3][0-3]$', ('').join(turn))) == self.MATCH_ONCE_ONLY
        turn.pop(0)
        turn = list(map(int, data))
        layer, row, column, token = turn 
        if(userRequestedTurn):
            return self._board[layer][row][column] == '_'
        else:
            return False

    ###########################################################################
    # @desc - Main turn control for the TTT Board. Pops the asterisk from the array for 
    #
    ###########################################################################
    def gamePlay(self, id, userTurn):
        userRequestedTurn = len(re.findall('^P[0-3][0-3][0-3][0-3]$', ('').join(userTurn))) == self.MATCH_ONCE_ONLY
        if (userRequestedTurn and self._currentTurn == id and int(userTurn[self.ID]) == id):
            userTurn.pop(0)
            self._command = list(map(int, userTurn))
            if (not self._winner and self.makePlayerMove()):
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
    # @desc - Checks for Win conditions going horizontally, either on a single plane
    #         or across the boards. Also if a win goes straight down this function
    #         uses shortcircuiting to reduce time complexity
    # @return - {boolean} if a win condition was met horizontally
    ###########################################################################
    def winHorizontal(self,):
        layer, row, column, token = self._command
        def test1():    
            #In single layer
            for data in self._board[layer][row]:
                if(data != token):
                    return False
            return True
        def test2():
            #from Top Layer to Bottom Layer
            for i in range(self.GRID_SIZE):
                if(self._board[i][row][i] != token):
                    return False
            return True
        def test3():
            #From Bottom Layer to Top Layer
            j = self.GRID_SIZE -1
            for i in range(self.GRID_SIZE -1, -1, -1):
                if(self._board[j][row][i] != token):
                    return False
                j -= 1   
            return True
        def test4():
            #Horizontal straight down between layers
            for i in range(self.GRID_SIZE):
                if(self._board[i][row][column] != token):
                    return False  
                return True
        return test1() or test2() or test3() or test4()

    ###########################################################################
    # @desc - Test for any form of Vertical win, Uses short circuiting to reduce
    #         time complexity of tests
    # @return - {boolean} if a win condition was met vertically
    ###########################################################################
    def winVertical(self):
        layer, row, column, token = self._command
        def test1():
            #in one layer
            for i in range(self.GRID_SIZE):
                if(self._board[layer][i][column] != token):
                    return False
            return True
        def test2():
            #between layers starting from top
            for i in range(self.GRID_SIZE):
                if(self._board[i][i][column] != token):
                    return False
            return True
        def test3():
            #between layers starting from bottom
            j = self.GRID_SIZE - 1
            for i in range(self.GRID_SIZE):
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
    def winDiagonal(self):
        layer, row, column, token = self._command
        def test1():
            #Left to right across all boards    
            for i in range(self.GRID_SIZE):
                if self._board[i][i][i] != token:
                    return False
            return True
        def test2():
            #Right to left across all boards
            j = self.GRID_SIZE - 1
            for i in range(self.GRID_SIZE):
                if(self._board[i][i][j] != token):
                    return False
                j -= 1
            return True
        def test3():
            #Left to right, single layer
            for i in range(self.GRID_SIZE):
                if(self._board[layer][i][i] != token):
                    return False
            return True
        def test4():
            #Right to left single layer
            j = self.GRID_SIZE - 1 
            for i in range(self.GRID_SIZE):
                if(self._board[layer][i][j] != token):
                    return False
                j -= 1
            return True
        def test5():
            #Bottom left to Top right across layers
            j = self.GRID_SIZE -1
            for i in range(self.GRID_SIZE):
                if(self._board[i][j][i] != token):
                    return False
                j -= 1
            return True
        def test6():
            #Bottom Right to Top Left across layers
            j = self.GRID_SIZE -1
            for i in range(self.GRID_SIZE):
                if(self._board[i][j][j] != token):
                    return False
                j -= 1
            return True

        return test1() or test2() or test3() or test4() or test5() or test6()

    ###########################################################################
    # @desc - Runs all commands for checking win conditions, if win condition
    #         is found, updates Winner status, and sets ID
    #         *if Minimum number of turns is not met, it won't check
    ###########################################################################
    def checkForWins(self):
        self._turnsTaken += 1
        if self._turnsTaken >= self.MINIMUM_TURNS_TO_WIN:
            if self.winDiagonal() or self.winHorizontal() or self.winVertical():
                self._winner = True
                self._winnerID = self._command[self.ID -1]
            
    ###########################################################################
    # @desc - Returns ID of player that will play next
    ###########################################################################
    def checkWhoseTurn(self):
        return self._currentTurn
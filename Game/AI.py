from Board import Board

class AI:
    def __init__(self, board: Board):
        self.__turn: int   = 0
        self.__board = board
        self.__minesCount  = board.get_mines_count()
        self.__boardMines  = board.get_board_mines()
        self.__boardFreq   = board.get_board_freq()
        self.__boardStates = board.get_board_state()
        self.__board_shapes = board.get_board_shape()
        self.__movesList   = []
        self.__markedList   = []
        self.__probabilities = [[-1.] * self.__board_shapes[1] for _ in range(self.__board_shapes[0])]
        self.__moves_Return = []

    def make_move(self):
        """
        The AI choose a cell to unlock and mark the cells that are 100% to be a mine
        :return: row, column
        """
        # For the first couple turn, let the AI cheats and choose a safe cell
        if self.__turn == 0:
            self.__turn += 1
            self.__moves_Return = [(0, 0)]
            return self.__moves_Return
        elif self.__turn >= 1:
            # This is the important part
            # 1. Look through all the numbered cells and find their neighbour
            edgeCells = {} # Use a dictionary so I don't have to use 'not in' again
            # TODO: Add some localization for faster decision
            for move in self.__movesList:
                potential_neighbour = self.__board.get_hidden_neighbour(move[0], move[1])
                for p in potential_neighbour:
                    edgeCells[p] = p

            print(edgeCells)
            self.calculate_probability()
            self.__turn += 1
            return self.__moves_Return

        pass

    def get_moves_list(self):
        return self.__movesList


    def calculate_probability(self):
        # Marked cells are 100% to be bomb
        self.__probabilities = [[-1.] * self.__board_shapes[1] for _ in range(self.__board_shapes[0])]
        self.fill_marked_probabilities()

        # Trivial deduction rule 1
        self.ruleOne()
        # Trivial deduction rule 2
        self.ruleTwo()

    def fill_marked_probabilities(self):
        for i in range(self.__board_shapes[0]):
            for j in range(self.__board_shapes[1]):
                self.__probabilities[i][j] = 100

    def ruleOne(self):
        """
        For each frequency cell if it has the same amount of hidden cells as the un-flagged bomb around it then flag it
        :return: None
        """
        for r, c in self.__movesList:
            un_flagged = self.__board.get_hidden_neighbour(r, c)
            flagged    = self.__board.get_flagged_neighbour(r, c)
            if len(un_flagged) + len(flagged) == self.__boardFreq[r][c]:
                # All the un-flagged are bomb -> flag them
                for n_r, n_c in un_flagged:
                    self.__probabilities[n_r][n_c] = 1
                    self.__boardStates[n_r][n_c] = 1


    def ruleTwo(self):
        """
        If a cell's frequency is the same as the number flagged cell around it, the remaining
        hidden square are 100% NOT bomb!

        :return: None
        """
        for r, c in self.__movesList:
            un_flagged = self.__board.get_hidden_neighbour(r, c)
            flagged    = self.__board.get_flagged_neighbour(r, c)
            if len(flagged) == self.__boardFreq[r][c]:
                # All the un-flagged are  NOT bomb -> Open them
                for n_r, n_c in un_flagged:
                    self.__probabilities[n_r][n_c] = 0
                    # self.__boardStates[n_r][n_c] = 2
                    self.__moves_Return.append((n_r, n_c))



class Moves:
    def __init__(self, row, col, turn):
        self.row = row
        self.col = col
        self.turn = turn
        self.movesID = turn * 10e4 + row * 10e2 + col

    def __eq__(self, other):
        return self.movesID == other.movesID

import time

from Board import Board
from nguyenpanda.swan import Color
from typing_extensions import List
import copy


class AI:
    def __init__(self, board: Board):
        self.__turn: int = 0
        self.__board = board
        self.__minesCount = board.get_mines_count()
        self.__boardMines = board.get_board_mines()
        self.__boardFreq = board.get_board_freq()
        self.__boardStates = board.get_board_state()
        self.__board_shapes = board.get_board_shape()


        self.__movesList = []
        self.__markedList = []
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
            self.print_probability()
            return self.__moves_Return
        elif self.__turn >= 1:
            # This is the important part
            # 1. Filter out the solved cells
            # 2. Look through all the numbered cells and find their neighbour
            self.filter_solved_cells()
            edgeCells = {}  # Use a dictionary so I don't have to use 'not in' again
            # TODO: Add some localization for faster decision
            for move in self.__movesList:
                potential_neighbour = self.__board.get_hidden_neighbour(move[0], move[1])
                for p in potential_neighbour:
                    edgeCells[p] = p

            # Update the probabilities for each cell and self.__moves_Return
            self.__moves_Return = []
            self.calculate_probability(edgeCells)

            # Loop
            self.__turn += 1
            return self.__moves_Return

        pass

    def filter_solved_cells(self):
        for i in range(len(self.__movesList) - 1, -1, -1):
            cell = self.__movesList[i]
            if self.__board.solved_cell(cell[0], cell[1]):
                self.__movesList.pop(i)

    def get_moves_list(self):
        return self.__movesList

    def calculate_probability(self, edgeCell):
        """
        Update the probabilities for
        :param edgeCell:
        :return:
        """
        # Marked cells are 100% to be bomb
        self.__probabilities = [[-1.] * self.__board_shapes[1] for _ in range(self.__board_shapes[0])]
        self.fill_marked_probabilities()
        self.fill_opened_probabilities()
        # Trivial deduction rule 1
        self.ruleOne()
        # Trivial deduction rule 2
        self.ruleTwo()

        # Only do this if there's no way to avoid having luck involved in decision, well in theory
        if len(self.__moves_Return) == 0:
            # Generate all possible arrangement
            # key: (row, column) - value: the frequency of that cell
            moveFreq = {}
            for r, c in self.__movesList:
                moveFreq[(r, c)] = self.__boardFreq[r][c]
                moveFreq[(r, c)] -= len(self.__board.get_flagged_neighbour(r, c))


            edgeMine = {}
            edgeList = []
            arrange_probability = {}
            # Base case before generation, all edge doesn't contain any bomb
            for r, c in edgeCell:
                edgeMine[(r, c)] = 0
                arrange_probability[(r, c)] = 0.
                if self.__boardStates[r][c] != 1:
                    edgeList.append((r, c))
            arrangementList = []
            print(Color["b"],edgeList)
            self.generate_arrangement(0, moveFreq, edgeList, edgeMine, arrangementList)
            print(len(arrangementList))



            num_arrange = len(arrangementList)

            for arrangement in arrangementList:
                for edge in edgeList:
                    arrange_probability[edge] += arrangement[edge]


            for edge in edgeList:
                arrange_probability[edge] /= num_arrange
                self.__probabilities[edge[0]][edge[1]] = arrange_probability[edge]
                if len(self.__moves_Return) == 0:
                    self.__moves_Return = [edge]
                # This edge cell has a smaller change to be a bomb
                elif arrange_probability[edge] < arrange_probability[self.__moves_Return[0]]:
                    self.__moves_Return = [edge]




    def fill_marked_probabilities(self):
        for i in range(self.__board_shapes[0]):
            for j in range(self.__board_shapes[1]):
                if self.__boardStates[i][j] == 1:
                    self.__probabilities[i][j] = 1

    def fill_opened_probabilities(self):
        for i in range(self.__board_shapes[0]):
            for j in range(self.__board_shapes[1]):
                if self.__boardStates[i][j] == 2:
                    self.__probabilities[i][j] = 0

    def ruleOne(self):
        """
        For each frequency cell if it has the same amount of hidden cells as the un-flagged bomb around it then flag it
        :return: None
        """
        for r, c in self.__movesList:
            un_flagged = self.__board.get_hidden_neighbour(r, c)
            flagged = self.__board.get_flagged_neighbour(r, c)
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
            flagged = self.__board.get_flagged_neighbour(r, c)
            if len(flagged) == self.__boardFreq[r][c]:
                # All the un-flagged are  NOT bomb -> Open them
                for n_r, n_c in un_flagged:
                    self.__probabilities[n_r][n_c] = 0
                    # self.__boardStates[n_r][n_c] = 2
                    self.__moves_Return.append((n_r, n_c))

    def generate_arrangement(self, i: int, moveFreq, edgeList, edgeMine, arrangeList: List):
        # 1st cell is a bomb
        self.generate_arrangement_helper(i, moveFreq, edgeList, edgeMine, isBomb=1,
                                         arrangeList=arrangeList)
        # 1st cell is not a bomb
        self.generate_arrangement_helper(i, moveFreq, edgeList, edgeMine, isBomb=0,
                                         arrangeList=arrangeList)

    def generate_arrangement_helper(self, i: int, moveFreq, edgeList, edgeMine, isBomb: int,
                                    arrangeList: List):
        """
        Generate and test all possible bomb arrangement that satisfy all
        neighbouring frequency cells of all edge cells
        :param i: the index traverse the edgeCell list
        :param moveFreq: A dictionary to store the leftover frequency of the neighbour of the edge cell
        :param edgeList: The list containing all edge cells
        :param edgeMine: A dictionary to store the assumption if the cell contains a bomb
        :param isBomb: Assumption that the i-th cell of the list is a bomb or not
        :param arrangeList: A list to store all possible arrangements
        :return:
        """
        temp_freq = copy.deepcopy(moveFreq)
        temp_mine = copy.deepcopy(edgeMine)
        # if i == 0:
        #     print(Color["CYAN"] +"="*25, isBomb)
        # else:
        #     print(Color["CYAN"] + "\t\t" + "=" * 25, isBomb)
        # # print(Color["b"],temp_freq)
        # print(Color["g"],temp_mine)
        try:
            curr_edge = edgeList[i]
        except:
            print("Index:", i)
            print(edgeList)
        # print("Curr eddge:",curr_edge)
        # If the cell is flagged is guaranteed to be a bomb
        if self.__boardStates[curr_edge[0]][curr_edge[1]] == 1:
            if isBomb == 0:  # The assumption is wrong, no need to traverse this path
                return

        if isBomb == 1:
            # Find the frequency neighbour of this edge cell
            # print(Color["r"]+"Bomb=1")
            temp_mine[curr_edge] = 1
            neighbours = self.__board.get_frequency_neighbours(curr_edge[0], curr_edge[1])
            for n in neighbours:
                if temp_freq[n] == 0:
                    # If this cell is a mine then the frequency will be greater than actual value
                    return  # This means that the assumption is wrong, no need to traverse this path
                temp_freq[n] -= 1  # Reduce the frequency
            # No more edge cell to check, meaning have generated all possibilities

        elif isBomb == 0:
            # print(Color["p"]+"Bomb=0")
            temp_mine[curr_edge] = 0



        # print(Color["b"], temp_freq)
        # print(Color["g"], temp_mine)
        if i == len(edgeList) - 1:

            if not all(value == 0 for value in temp_freq.values()):
                # print(Color["r"]+ "This arrangement does NOT satisfy the frequency")
                return
            # print(Color["r"]+ "This arrangement DOES satisfy the frequency")
            arrangeList.append(temp_mine)
            return
        self.generate_arrangement_helper(i + 1, temp_freq, edgeList, temp_mine, isBomb=1,
                                         arrangeList=arrangeList)
        self.generate_arrangement_helper(i + 1, temp_freq, edgeList, temp_mine, isBomb=0,
                                         arrangeList=arrangeList)

    def print_probability(self):
        print(Color["p"])
        print(Color["p"] + "=" * 30)
        for row in self.__probabilities:
            print(row)


class Moves:
    def __init__(self, row, col, turn):
        self.row = row
        self.col = col
        self.turn = turn
        self.movesID = turn * 10e4 + row * 10e2 + col

    def __eq__(self, other):
        return self.movesID == other.movesID

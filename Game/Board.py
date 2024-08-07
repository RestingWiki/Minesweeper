import random
from nguyenpanda.swan import Color
import pygame
from typing_extensions import Callable


class Board:
    # @formatter:off
    # Small board
    BOARD_WIDTH_S  = 6
    BOARD_HEIGHT_S = 6
    BOARD_MINES_S  = 3
    # Medium board
    BOARD_WIDTH_M  = 16
    BOARD_HEIGHT_M = 1
    BOARD_MINES_M  = 40
    # Large board
    BOARD_WIDTH_L  = 30
    BOARD_HEIGHT_L = 1
    BOARD_MINES_L  = 99
    # @formatter: on


    def __init__(self):
        self.__board_width   = self.BOARD_WIDTH_S
        self.__board_height  = self.BOARD_HEIGHT_S
        self.__mines_counts = self.BOARD_MINES_S
        self.__board_mines    = [[0] * self.__board_width for _ in range(self.__board_height)]
        self.__board_freq     = [[0] * self.__board_width for _ in range(self.__board_height)]
        # 0: Neutral 1: Marked 2: Opened
        self.__board_state    = [[0] * self.__board_width for _ in range(self.__board_height)]
        self.fillBoard(self.__mines_counts)
        self.fillFrequency()
        self.printBoards()

    def fillBoard(self, numMines: int):
        mines_dict = {}
        while len(mines_dict) < numMines:
            idx = random.randint(0, self.__board_width * self.__board_height -1)
            mines_dict[idx] = idx
            row = idx // self.__board_width
            col = idx % self.__board_width
            self.__board_mines[row][col] = 1

    def fillFrequency(self):
        for i in range(self.__board_height):
            for j in range(self.__board_width):
                neighbourList = self.getNeighbour(i, j)
                for n_x, n_y in neighbourList:
                    if self.__board_mines[n_x][n_y]:
                        self.__board_freq[i][j] += 1

    def getNeighbour(self, row: int, col: int, func: Callable = None):
        dX = [-1, 0, 1]
        dY = [-1, 0, 1]
        neighbourList = []
        for dx in dX:
            for dy in dY:
                if dx == dy == 0: continue
                if self.inBoard(row + dx, col + dy):
                    neighbourList.append((row + dx, col + dy))

        return neighbourList

    def get_hidden_neighbour(self, row: int, col: int):
        """
        Return the neighbours that are not marked or opened
        :param row:
        :param col:
        :return:
        """
        dX = [-1, 0, 1]
        dY = [-1, 0, 1]
        neighbourList = []
        for dx in dX:
            for dy in dY:
                if dx == dy == 0: continue
                if self.inBoard(row + dx, col + dy) and self.__board_state[row + dx][col + dy] == 0:
                    neighbourList.append((row + dx, col + dy))

        return neighbourList

    def get_flagged_neighbour(self, row: int, col: int):
        """
        Return the neighbours that are not marked or opened
        :param row:
        :param col:
        :return:
        """
        dX = [-1, 0, 1]
        dY = [-1, 0, 1]
        neighbourList = []
        for dx in dX:
            for dy in dY:
                if dx == dy == 0: continue
                if self.inBoard(row + dx, col + dy) and self.__board_state[row + dx][col + dy] == 1:
                    neighbourList.append((row + dx, col + dy))

        return neighbourList
    def get_friendly_neighbours(self, row: int, col: int):
        dX = [-1, 0, 1]
        dY = [-1, 0, 1]
        neighbourList = []
        for dx in dX:
            for dy in dY:
                if dx == dy == 0: continue
                if self.__board_freq[row][col] > 0: break
                if self.inBoard(row + dx, col + dy) and self.__board_mines[row+dx][col+dy] != 1:
                    neighbourList.append((row + dx, col + dy))

        return neighbourList

    def inBoard(self, row: int, col:int):
        return 0 <= row < self.__board_height and 0 <= col < self.__board_width


    def winning_check(self):
        safeCells: int = self.__board_width * self.__board_height - self.__mines_counts
        count: int = 0
        # Count opended space
        for r in range(self.__board_height):
            for c in range(self.__board_width):
                if self.__board_state[r][c] == 2:
                    count += 1
        return safeCells == count
    def printBoards(self):
        print(Color["r"])

        for row in self.__board_mines:
            print(row)

        print(Color["y"] + "="*30)
        print(Color["r"])
        for row in self.__board_freq:
            print(row)

    def get_board_mines(self):
        return self.__board_mines

    def get_board_freq(self):
        return self.__board_freq

    def get_board_state(self):
        return self.__board_state

    def get_mines_count(self):
        return self.__mines_counts
    def get_board_shape(self):
        return self.__board_height, self.__board_width

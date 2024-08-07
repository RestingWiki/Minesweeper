from collections import deque

import pygame
import time

from typing_extensions import List

from Board import Board
from AI import AI

# Pygame initialization
pygame.init()

# Constants for the board and window size
TILE_SIZE = 40
BOARD_MARGIN = 10
TOP_WINDOW_HEIGHT = 60
WIDTH = Board.BOARD_WIDTH_S * TILE_SIZE + 2 * BOARD_MARGIN
HEIGHT = Board.BOARD_HEIGHT_S * TILE_SIZE + 2 * BOARD_MARGIN + TOP_WINDOW_HEIGHT
SCREEN_SIZE = (WIDTH, HEIGHT)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (77, 84, 91)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
# Additional colors
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (165, 42, 42)
PINK = (255, 192, 203)
LIGHT_GREY = (113, 120, 127)
DARK_GREY = (35, 42, 49)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
GOLD = (255, 215, 0)
SHADOW = (48, 48, 48)
HIGHLIGHT = (192, 192, 192)
# Colors for frequency count from light to dark
FREQUENCY_COLORS = [
    (173, 216, 230),  # Light Blue
    (135, 206, 235),  # Sky Blue
    (0, 191, 255),  # Deep Sky Blue
    (30, 144, 255),  # Dodger Blue
    (0, 0, 255),  # Blue
    (0, 0, 139),  # Dark Blue
    (0, 100, 0),  # Dark Green
    (255, 165, 0),  # Orange
    (255, 0, 0)  # Red
]

# Set up the display
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Minesweeper")

# Create a Board instance
board = Board()

# Use AI?
USE_AI: bool = True
if USE_AI:
    AI = AI(board)

# Player status
ALIVE: bool = True

# Game variables
start_time = time.time()
total_flags = board.BOARD_MINES_S
flags_left = total_flags

# Seven-segment display segment positions
SEGMENT_POSITIONS = {
    'A': [(2, 0), (3, 0), (4, 0)],
    'B': [(5, 1), (5, 2), (5, 3)],
    'C': [(5, 4), (5, 5), (5, 6)],
    'D': [(2, 7), (3, 7), (4, 7)],
    'E': [(1, 4), (1, 5), (1, 6)],
    'F': [(1, 1), (1, 2), (1, 3)],
    'G': [(2, 3), (3, 3), (4, 3)]
}

# Digits to segments mapping
DIGIT_TO_SEGMENTS = {
    0: ['A', 'B', 'C', 'D', 'E', 'F'],
    1: ['B', 'C'],
    2: ['A', 'B', 'G', 'E', 'D'],
    3: ['A', 'B', 'G', 'C', 'D'],
    4: ['F', 'G', 'B', 'C'],
    5: ['A', 'F', 'G', 'C', 'D'],
    6: ['A', 'F', 'G', 'E', 'D', 'C'],
    7: ['A', 'B', 'C'],
    8: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    9: ['A', 'B', 'C', 'D', 'F', 'G']
}


# Function to draw a single digit as a seven-segment display
def draw_digit(screen, digit, top_left, size):
    segment_length = size // 6
    segment_thickness = size // 10
    color = RED

    for segment in DIGIT_TO_SEGMENTS[digit]:
        for (dx, dy) in SEGMENT_POSITIONS[segment]:
            rect = pygame.Rect(
                top_left[0] + dx * segment_length,
                top_left[1] + dy * segment_length,
                segment_thickness,
                segment_thickness
            )
            pygame.draw.rect(screen, color, rect)


# Function to draw a number as a seven-segment display
def draw_seven_segment_flag(screen, number, top_left, size, digits=3):
    num_str = str(number).zfill(digits)
    digit_width = size // digits + 25  # Added extra space between digits
    for i, digit in enumerate(num_str):
        draw_digit(screen, int(digit), (top_left[0] + i * digit_width, top_left[1]), size)


def draw_seven_segment_time(screen, number, top_left, size, digits=3):
    num_str = str(number).zfill(digits)
    digit_width = size // digits + 25  # Added extra space between digits
    for i, digit in enumerate(num_str):
        draw_digit(screen, int(digit), (top_left[0] + i * digit_width, top_left[1]), size)


def draw_top_window():
    # Draw the top window background
    top_window_rect = pygame.Rect(0, 0, WIDTH, TOP_WINDOW_HEIGHT)
    pygame.draw.rect(screen, DARK_GREY, top_window_rect)

    # Draw the elapsed time
    elapsed_time = int(time.time() - start_time)
    draw_seven_segment_flag(screen, elapsed_time, (20, 10), TOP_WINDOW_HEIGHT - 20)

    # Draw the flags left
    draw_seven_segment_time(screen, flags_left, (WIDTH - 140, 10), TOP_WINDOW_HEIGHT - 20)


# Main loop
running: bool = True


def unlock_empty_neighbour(row, col, boardState):
    """
    This function is responsible for
    1. Performing BFS from chosen cell to unlock empty cells
    2. Mark the neighbours as '2: Opened'
    :param row: row
    :param col: column
    :param boardState: current state of the entire board  (0: Neutral, 1: Marked, 2: Opened)
    :return: None
    """
    neighbour = deque(board.get_friendly_neighbours(row, col))
    # For each neighbour
    while neighbour:
        # Pop and mark
        curr = neighbour.popleft()
        boardState[curr[0]][curr[1]] = 2
        # Find new neighbours that are not bombs
        new_neighbour = board.get_friendly_neighbours(curr[0], curr[1])
        for new_n in new_neighbour:
            # Add neighbour if
            # 1. Not already in the deque
            # 2. Not already been opened or still hidden
            if (new_n not in neighbour and boardState[new_n[0]][new_n[1]] != 2):
                neighbour.append(new_n)


def chooseCell(row, col, boardState, boardMines):
    global ALIVE
    print("Left mouse button clicked")
    # Hit a bomb!
    if boardMines[row][col] == 1:
        ALIVE = False

    # Safe
    boardState[row][col] = 2
    if ALIVE:
        unlock_empty_neighbour(row, col, boardState)


"""
            _    ___        ____ _____ _   _ _____ _____
           / \  |_ _|      / ___|_   _| | | |  ___|  ___|
          / _ \  | |       \___ \ | | | | | | |_  | |_
         / ___ \ | |        ___) || | | |_| |  _| |  _|
        /_/   \_\___|      |____/ |_|  \___/|_|   |_|
"""


def unlock_empty_neighbour_AI(row: int, col: int, boardState: List, boardFreq: List, movesList: List):
    """
    This function is responsible for
    1. Performing BFS from chosen cell to unlock empty cells
    2. Mark the neighbours as '2: Opened'
    :param row: row
    :param col: column
    :param boardState: current state of the entire board  (0: Neutral, 1: Marked, 2: Opened)
    :return: None
    """
    neighbour = deque(board.get_friendly_neighbours(row, col))
    # For each neighbour
    while neighbour:
        # Pop and mark
        curr = neighbour.popleft()
        boardState[curr[0]][curr[1]] = 2
        # If it's a numbered cell add it to the list for probability calculation
        if boardFreq[curr[0]][curr[1]] > 0 and curr not in movesList :
            movesList.append(curr)

        # Find new neighbours that are not bombs
        new_neighbour = board.get_friendly_neighbours(curr[0], curr[1])
        for new_n in new_neighbour:
            # Add neighbour if
            # 1. Not already in the deque
            # 2. Not already been opened or still hidden or a mine!
            if new_n not in neighbour and boardState[new_n[0]][new_n[1]] != 2:
                neighbour.append(new_n)


def choose_cell_AI(row: int, col: int, boardState: List, boardMines: List, boardFreq: List, movesList: List):
    """

    :param row: row
    :param col: column
    :param boardState: current state of the entire board  (0: Neutral, 1: Marked, 2: Opened)
    :param boardMines:
    :param movesList:
    :return:
    """
    global ALIVE
    # Hit a bomb!
    if boardMines[row][col] == 1:
        ALIVE = False

    # Safe
    boardState[row][col] = 2
    if ALIVE:
        move = (row, col)
        if boardFreq[row][col] > 0 and move not in movesList:
            movesList.append(move)
        unlock_empty_neighbour_AI(row, col, boardState, boardFreq, movesList)

while running:
    """
    
    """
    if USE_AI:
        # Retrieve the current state of the board
        boardState = board.get_board_state()
        boardMines = board.get_board_mines()
        boardFreq = board.get_board_freq()
        movesList = AI.get_moves_list() # A reference to the possible moves
        # Makes a move
        print(movesList)
        for row, col in AI.make_move():
            choose_cell_AI(row, col, boardState, boardMines, boardFreq, movesList)

    # Player event handling
    elif not USE_AI:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                col = (location[0] - BOARD_MARGIN) // TILE_SIZE
                row = (location[1] - BOARD_MARGIN - TOP_WINDOW_HEIGHT) // TILE_SIZE
                if 0 <= col < board.BOARD_WIDTH_S and 0 <= row < board.BOARD_HEIGHT_S:
                    boardState = board.get_board_state()
                    boardMines = board.get_board_mines()

                    if event.button == 1:  # Left mouse button
                        chooseCell(row, col, boardState, boardMines)


                    elif event.button == 3:  # Right mouse button
                        print("Right mouse button clicked")
                        if boardState[row][col] == 0 and flags_left > 0:  # Only place a flag on a closed tile
                            boardState[row][col] = 1
                            flags_left -= 1
                        elif boardState[row][col] == 1:  # Remove flag
                            boardState[row][col] = 0
                            flags_left += 1

    """
    This part onwards only responsible for updating the graphics
    """
    # Fill the screen with white background
    screen.fill(WHITE)

    # Draw the top window
    draw_top_window()

    # Draw the Minesweeper board
    for row in range(board.BOARD_HEIGHT_S):
        for col in range(board.BOARD_WIDTH_S):
            # Create a rectangle for each tile
            boardState = board.get_board_state()
            rect = pygame.Rect(BOARD_MARGIN + col * TILE_SIZE, BOARD_MARGIN + row * TILE_SIZE + TOP_WINDOW_HEIGHT,
                               TILE_SIZE, TILE_SIZE)

            # Default tile
            if boardState[row][col] == 0:
                pygame.draw.rect(screen, GREY, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

            # Marked tile (right-click)
            elif boardState[row][col] == 1:
                pygame.draw.rect(screen, LIGHT_GREY, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
                pygame.draw.line(screen, RED, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(screen, RED, rect.topright, rect.bottomleft, 2)

            # Opened tile (left-click)
            elif boardState[row][col] == 2:
                pygame.draw.rect(screen, DARK_GREY, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

                # Draw a red circle if there's a mine
                if board.get_board_mines()[row][col] == 1:
                    pygame.draw.circle(screen, RED, rect.center, TILE_SIZE // 4)

                # Display the frequency count of adjacent mines
                freq = board.get_board_freq()[row][col]
                if freq > 0:
                    font = pygame.font.Font(None, 36)
                    color = FREQUENCY_COLORS[freq]
                    text = font.render(str(freq), True, color)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
            else:
                raise Exception("How did we get here?!")

    # Update the display
    pygame.display.flip()
    if not ALIVE:
        # TODO: ADD DEATH MESSAGE
        running = False
        pass
    if board.winning_check():
        # TODO: ADD WINNING MESSAGE
        time.sleep(10000)
        running = False

    time.sleep(1)
# Quit Pygame
pygame.quit()

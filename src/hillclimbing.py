import copy
import os
import random

def read_sudoku_file():
    """
    Reads Sudoku puzzles from multiple text files in a folder.
    Each file contains a single 9x9 puzzle.
    Returns a list of 9x9 boards.
    """
    boards = []
    folder_path=os.path.join(os.path.dirname(__file__), '..', 'data')
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            board = [[int(num) for num in line.strip()] for line in file if line.strip()]
            boards.append(board)
    return boards

def initialize_board(board):
    """
    Initializes the board with random values for non-fixed cells.
    Fixed cells are stored in a separate board.
    """
    fixed_board = [[cell != 0 for cell in row] for row in board]
    for row in range(9):
        non_fixed = [col for col in range(9) if not fixed_board[row][col]]
        available_numbers = list(set(range(1, 10)) - set(board[row]))
        random.shuffle(available_numbers)
        for col in non_fixed:
            board[row][col] = available_numbers.pop()
    return board, fixed_board

def heuristic(board):
    """
    Calculates the number of conflicts in the Sudoku board.
    Conflicts are counted in rows, columns, and 3x3 subgrids.
    """
    conflicts = 0

    # Check rows and columns
    for i in range(9):
        row_conflicts = 9 - len(set(board[i]))
        col_conflicts = 9 - len(set(board[j][i] for j in range(9)))
        conflicts += row_conflicts + col_conflicts

    # Check 3x3 subgrids
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            subgrid = []
            for i in range(3):
                for j in range(3):
                    subgrid.append(board[box_row + i][box_col + j])
            conflicts += 9 - len(set(subgrid))

    return conflicts

def get_neighbors(board, fixed_board):
    """
    Generates neighboring boards by swapping two numbers in the same row,
    but only for cells that are not fixed (i.e., initially 0).
    """
    neighbors = []
    for row in range(9):
        # Find indices of non-fixed cells in the row
        non_fixed = [col for col in range(9) if not fixed_board[row][col]]
        if len(non_fixed) > 1:
            for i in range(len(non_fixed)):
                for j in range(i + 1, len(non_fixed)):
                    new_board = copy.deepcopy(board)
                    # Swap two numbers
                    new_board[row][non_fixed[i]], new_board[row][non_fixed[j]] = (
                        new_board[row][non_fixed[j]],
                        new_board[row][non_fixed[i]],
                    )
                    neighbors.append(new_board)
    return neighbors

def hill_climbing(board):
    """
    Solves the Sudoku puzzle using the hill climbing algorithm.
    """
    current_board, fixed_board = initialize_board(board)
    current_heuristic = heuristic(current_board)


    while True:
        neighbors = get_neighbors(current_board, fixed_board)
        if not neighbors:
            break

        # Evaluate neighbors
        next_board = None
        next_heuristic = float('inf')
        for neighbor in neighbors:
            h = heuristic(neighbor)
            if h < next_heuristic:
                next_board = neighbor
                next_heuristic = h

        # If no improvement, stop
        if next_heuristic >= current_heuristic:
            break

        # Move to the better neighbor
        current_board = next_board
        current_heuristic = next_heuristic

    return current_board, current_heuristic

# Example usage
if __name__ == "__main__":
    # Read puzzles from file
    puzzles = read_sudoku_file()

    # Solve each puzzle
    for i, puzzle in enumerate(puzzles):
        print(f"Solving puzzle {i + 1}...")
        solution, h = hill_climbing(puzzle)
        if h == 0:
            print("Solution found:")
            for row in solution:
                print(row)
        else:
            print("No solution found with hill climbing.")
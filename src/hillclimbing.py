import copy
import os
import random
import time
import psutil
from collections import deque

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

def validate_board(board):
    for i in range(9):
        if len(set(board[i]) - {0}) != len([num for num in board[i] if num != 0]):
            raise ValueError(f"Conflict found in row {i + 1}")
        col = [board[j][i] for j in range(9)]
        if len(set(col) - {0}) != len([num for num in col if num != 0]):
            raise ValueError(f"Conflict found in column {i + 1}")

    # Check 3x3 subgrids
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            subgrid = []
            for i in range(3):
                for j in range(3):
                    subgrid.append(board[box_row + i][box_col + j])
            if len(set(subgrid) - {0}) != len([num for num in subgrid if num != 0]):
                raise ValueError(f"Conflict found in 3x3 subgrid starting at ({box_row + 1}, {box_col + 1})")
    return True


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
    board = copy.deepcopy(board)
    current_board, fixed_board = initialize_board(board)
    current_heuristic = heuristic(current_board)
    blank_squares = sum(row.count(0) for row in fixed_board)
    max_iterations = 9 * (blank_squares ** 2)
    iteration = 0
    recent_states = deque(maxlen=20)
    # Main loop
    while iteration < max_iterations:
        neighbors = get_neighbors(current_board, fixed_board)
        if not neighbors:
            break

        # Evaluate neighbors
        next_board = None
        next_heuristic = float('inf')
        for neighbor in neighbors:
            if neighbor in recent_states:  # Remove neighbour if is in recent_states
                neighbors.remove(neighbor)
                continue
            h = heuristic(neighbor)
            if h < next_heuristic:
                next_board = neighbor
                next_heuristic = h

        # If no improvement, pick a random move
        if next_board is None or next_heuristic >= current_heuristic:
            next_board = random.choice(neighbors)
            next_heuristic = heuristic(next_board)

        # Move to the next board
        current_board = next_board
        current_heuristic = next_heuristic
        recent_states.append(current_board)
        # Stop if a solution is found
        if current_heuristic == 0:
            break

        iteration += 1
    return current_board, current_heuristic, iteration

def save_solution_to_file(solution, puzzle_index):
    """
    Saves the solution to a text file in the 'solutions' folder.
    Creates the folder if it does not exist and overwrites the file if it exists.
    """
    # Define the folder and file path
    folder_path = os.path.join(os.path.dirname(__file__), '..', 'solutions')
    os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
    file_path = os.path.join(folder_path, f"solution_{puzzle_index + 1}.txt")

    # Write the solution to the file
    with open(file_path, 'w') as file:
        for row in solution:
            file.write(''.join(map(str, row)) + '\n')


# Example usage
if __name__ == "__main__":
    # Start measuring processing time and memory usage
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss

    # Read puzzles from file
    puzzles = read_sudoku_file()
    solutionN=0
    # Solve each puzzle
    for i, puzzle in enumerate(puzzles):
        puzzle_start_time = time.time()
        try:
            validate_board(puzzle)
        except ValueError as e:
            print(f"Puzzle {i + 1} is invalid: {e}\nNo solution found with hill climbing. Continuing...")
            continue
        #Runs hill climbing algorithm for 3 iterations
        for n in range(0,3):
            print(f"Solving puzzle {i + 1}, attempt {n+1}...")
            solution, h, iterations = hill_climbing(puzzle)
            # Loop until a solution is found or max iterations reached
            if h==0:
                break
        if h == 0:
            puzzle_end_time = time.time()
            process_time = puzzle_end_time - puzzle_start_time
            print(f"Solution found, iterations: {iterations}\nTime taken: {round(process_time,3)}s\nSolution:")
            for row in solution:
                print(row)
            save_solution_to_file(solution, i)
            solutionN+=1
        else:
            print("No solution found with hill climbing.")

    # Measure processing time and memory usage
    end_time = time.time()
    end_memory = process.memory_info().rss

    # Calculate processing time and memory used
    processing_time = end_time - start_time
    memory_used = (end_memory - start_memory) / (1024 * 1024)  # Convert to MB

    # Print results
    print(f"\nTotal Processing Time: {processing_time:.2f} seconds")
    print(f"Memory Used: {memory_used:.2f} MB")
    print(f"Total solutions found: {solutionN}")
    if solutionN==0:
        print("No solutions found.")
    elif solutionN==10:
        print("All solutions found!")
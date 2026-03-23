import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projects.shared.tictactoe import TicTacToe
from projects.shared.db import get_connection, load_q_values
from projects.model_A.q_learning_agent import QLearningAgent

def play_human_vs_ai():
    print("Welcome to Tic-Tac-Toe vs Continuous AI (Model A)!")

    # Try to load Q-Table if DB is available
    q_table = {}
    try:
        q_table = load_q_values()
        if not q_table:
             print("\n[!] The AI's brain (Q-table) is completely empty. It will play randomly!")
        else:
             print(f"\n[+] Loaded AI brain with {len(q_table)} state-action pairs.")
    except Exception as e:
        print(f"\n[!] Could not connect to the database to load the Q-table. ({e})")
        print("    Make sure your local Postgres is running, or that you've downloaded the cache.")
        print("    The AI will play completely randomly for this match.\n")

    # The AI should exploit its knowledge, not explore
    ai_agent = QLearningAgent(q_table=q_table, epsilon=0.0)
    env = TicTacToe()

    print("\nBoard positions are numbered 0-8 like this:")
    env.print_board_nums()
    print("\nYou are 'X'. The AI is 'O'.\n")

    letter = 'X' # Human goes first

    while env.empty_squares():
        if letter == 'X':
            # Human Turn
            valid_move = False
            while not valid_move:
                try:
                    square = input("Your turn (enter a spot 0-8): ")
                    if square.lower() == 'q':
                        print("Quitting.")
                        return
                    square = int(square)
                    if square not in env.available_moves():
                        print("Invalid move. Spot is taken or out of bounds. Try again.")
                    else:
                        valid_move = True
                except ValueError:
                    print("Invalid input. Please enter a number from 0 to 8.")
            action = square
        else:
            # AI Turn
            print("AI is thinking...")
            state = env.get_state()
            available_actions = env.available_moves()
            action = ai_agent.choose_action(state, available_actions)

        env.make_move(action, letter)
        print(f"\nMove: {letter} placed on square {action}")
        env.print_board()
        print("")

        if env.current_winner:
            if letter == 'X':
                print("Congratulations! You won!")
            else:
                print("The AI won! Better luck next time.")
            return

        # Switch turns
        letter = 'O' if letter == 'X' else 'X'

    print("It's a tie!")

if __name__ == '__main__':
    play_human_vs_ai()

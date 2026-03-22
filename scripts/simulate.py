import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projects.shared.tictactoe import TicTacToe
from projects.shared.db import init_db, load_q_values, record_match
from projects.model_A.q_learning_agent import QLearningAgent
from projects.model_B.random_agent import RandomAgent

def simulate_game(agent_x, agent_o, env):
    env.board = [' ' for _ in range(9)]
    env.current_winner = None
    letter = 'X'
    total_moves = 0

    while env.empty_squares():
        state = env.get_state()
        available_actions = env.available_moves()

        if letter == 'X':
            action = agent_x.choose_action(state, available_actions)
        else:
            action = agent_o.choose_action(state, available_actions)

        if action is None:
            break

        env.make_move(action, letter)
        total_moves += 1

        if env.current_winner:
            break

        letter = 'O' if letter == 'X' else 'X'

    return env.current_winner, total_moves

if __name__ == '__main__':
    print("Starting Simulation Session...")

    init_db()

    # Load previous knowledge (No exploration this time, strict exploitation)
    q_table = load_q_values()
    agent_a = QLearningAgent(q_table=q_table, epsilon=0.0) # Epsilon 0.0 -> no random moves!
    agent_b = RandomAgent()

    env = TicTacToe()

    num_episodes = 100
    wins_a = 0
    wins_b = 0
    ties = 0

    print(f"Running {num_episodes} evaluation games: Model A (Q-Learning) vs Model B (Random)")
    for i in range(num_episodes):
        if i % 2 == 0:
            winner, moves = simulate_game(agent_a, agent_b, env)
            winner_name = 'Model_A' if winner == 'X' else ('Model_B' if winner == 'O' else 'Tie')
            record_match('Model_A', 'Model_B', winner, moves)
        else:
            winner, moves = simulate_game(agent_b, agent_a, env)
            winner_name = 'Model_B' if winner == 'X' else ('Model_A' if winner == 'O' else 'Tie')
            record_match('Model_B', 'Model_A', winner, moves)

        if winner_name == 'Model_A':
            wins_a += 1
        elif winner_name == 'Model_B':
            wins_b += 1
        else:
            ties += 1

    print(f"Simulation Complete! Model A Wins: {wins_a}, Model B Wins: {wins_b}, Ties: {ties}")
    win_rate = (wins_a / num_episodes) * 100
    print(f"Model A Win Rate: {win_rate}%")

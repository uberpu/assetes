import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projects.shared.tictactoe import TicTacToe
from projects.shared.db import init_db, save_q_values, load_q_values, record_match
from projects.model_A.q_learning_agent import QLearningAgent
from projects.model_B.random_agent import RandomAgent

def play_game(agent_x, agent_o, env, train_x=False, train_o=False):
    env.board = [' ' for _ in range(9)]
    env.current_winner = None
    letter = 'X'
    total_moves = 0

    # Store history for delayed rewards
    history_x = []
    history_o = []

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

        if letter == 'X':
            history_x.append((state, action))
        else:
            history_o.append((state, action))

        if env.current_winner:
            break

        letter = 'O' if letter == 'X' else 'X'

    # Game Over! Assign Rewards
    reward_x = 0
    reward_o = 0

    if env.current_winner == 'X':
        reward_x = 1
        reward_o = -1
    elif env.current_winner == 'O':
        reward_x = -1
        reward_o = 1
    else: # Tie
        reward_x = 0.5
        reward_o = 0.5

    # Update Q-Tables (Train backwards from the end)
    if train_x:
        for state, action in reversed(history_x):
            agent_x.update_q_value(state, action, reward_x, None, []) # Simple update for terminal/prop
            reward_x *= agent_x.gamma # Discount back in time

    if train_o:
        for state, action in reversed(history_o):
            agent_o.update_q_value(state, action, reward_o, None, [])
            reward_o *= agent_o.gamma

    return env.current_winner, total_moves

if __name__ == '__main__':
    print("Starting Training Session...")

    # Ensure tables exist
    init_db()

    # Load previous knowledge
    q_table = load_q_values()
    agent_a = QLearningAgent(q_table=q_table, epsilon=0.3) # Model A: Learns
    agent_b = RandomAgent()                                 # Model B: Random Opponent

    env = TicTacToe()

    # Run 500 training matches
    num_episodes = 500
    wins_a = 0
    wins_b = 0
    ties = 0

    print(f"Running {num_episodes} games: Model A (Q-Learning) vs Model B (Random)")
    for i in range(num_episodes):
        # Swap who goes first
        if i % 2 == 0:
            winner, moves = play_game(agent_a, agent_b, env, train_x=True, train_o=False)
            winner_name = 'Model_A' if winner == 'X' else ('Model_B' if winner == 'O' else 'Tie')
            record_match('Model_A', 'Model_B', winner, moves)
        else:
            winner, moves = play_game(agent_b, agent_a, env, train_x=False, train_o=True)
            winner_name = 'Model_B' if winner == 'X' else ('Model_A' if winner == 'O' else 'Tie')
            record_match('Model_B', 'Model_A', winner, moves)

        if winner_name == 'Model_A':
            wins_a += 1
        elif winner_name == 'Model_B':
            wins_b += 1
        else:
            ties += 1

    print(f"Training Complete! Model A Wins: {wins_a}, Model B Wins: {wins_b}, Ties: {ties}")

    # Save acquired knowledge back to Postgres
    save_q_values(agent_a.q_table)
    print("Q-table saved to DB.")

    # Append summary to training log
    import datetime
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'training_log.md')

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"| {timestamp} | {num_episodes} | {wins_a} | {wins_b} | {ties} |\n"

    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("# Model A (Q-Learning) Training Log\n\n")
            f.write("| Timestamp | Episodes | Model A Wins | Model B Wins | Ties |\n")
            f.write("|---|---|---|---|---|\n")

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    print(f"Appended training summary to {log_file}")

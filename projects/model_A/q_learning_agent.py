import random
import math

class QLearningAgent:
    def __init__(self, epsilon=0.1, alpha=0.5, gamma=0.9, q_table=None):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = q_table if q_table is not None else {}

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state, available_actions):
        if not available_actions:
            return None

        # Explore
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_actions)

        # Exploit
        q_values = [self.get_q_value(state, action) for action in available_actions]
        max_q = max(q_values)

        # If there are multiple actions with the same max Q-value, pick randomly among them
        best_actions = [a for a, q in zip(available_actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def update_q_value(self, state, action, reward, next_state, next_available_actions):
        current_q = self.get_q_value(state, action)

        max_next_q = 0.0
        if next_available_actions:
            max_next_q = max([self.get_q_value(next_state, next_action) for next_action in next_available_actions])

        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q

import random

class RandomAgent:
    def __init__(self):
        pass

    def choose_action(self, state, available_actions):
        if not available_actions:
            return None
        return random.choice(available_actions)

import os
import pickle
import random


class RLAgent:
    """Q-Learning agent for n-puzzle."""

    ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

    def __init__(self):
        self.Q = {}
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 1.0

    def choose_action(self, state: str) -> str:
        self._ensure_state(state)
        if random.random() < self.epsilon:
            return random.choice(self.ACTIONS)
        state_q = self.Q[state]
        return max(state_q, key=state_q.get)

    def update(self, state: str, action: str, reward: int, next_state: str):
        self._ensure_state(state)
        self._ensure_state(next_state)
        predict = self.Q[state][action]
        target = reward + self.gamma * max(self.Q[next_state].values())
        self.Q[state][action] = predict + self.alpha * (target - predict)

    def _ensure_state(self, state: str):
        if state not in self.Q:
            self.Q[state] = {a: 0.0 for a in self.ACTIONS}
        else:
            for a in self.ACTIONS:
                if a not in self.Q[state]:
                    self.Q[state][a] = 0.0

    def save_q_table(self, filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            pickle.dump(self.Q, f)

    def load_q_table(self, filename: str):
        try:
            with open(filename, "rb") as f:
                self.Q = pickle.load(f)
            print("Q-Table loaded successfully!")
        except FileNotFoundError:
            print("Q-Table file not found, starting fresh!")
            self.Q = {}
        except Exception as e:
            print(f"Error loading Q-Table: {e}")

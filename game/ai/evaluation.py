"""Evaluate a trained Q-Learning agent on the n-puzzle."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.ai.puzzle_env import PuzzleEnv
from game.ai.rl_agent import RLAgent


def evaluate(agent: RLAgent, env: PuzzleEnv, episodes: int):
    solved = 0
    total_steps = 0

    for episode in range(episodes):
        env.reset()
        state = env.get_state()
        steps = 0

        while not env.is_solved() and steps <= 500:
            action = agent.choose_action(state)
            env.step(action)
            state = env.get_state()
            steps += 1

        if env.is_solved():
            solved += 1
        total_steps += steps

    print("Evaluation complete.")
    print(f"Solved {solved} out of {episodes} episodes.")
    print(f"Average steps per episode: {total_steps / episodes:.2f}")


def main():
    env = PuzzleEnv(3)
    agent = RLAgent()

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    q_table_path = os.path.join(base_dir, "res", "data", "qtable.pkl")

    agent.load_q_table(q_table_path)
    evaluate(agent, env, 10000)


if __name__ == "__main__":
    main()

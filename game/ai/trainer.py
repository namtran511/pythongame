"""Q-Learning trainer for the n-puzzle agent."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.ai.puzzle_env import PuzzleEnv
from game.ai.rl_agent import RLAgent


def main():
    env = PuzzleEnv(3)
    agent = RLAgent()

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    q_table_path = os.path.join(base_dir, "res", "data", "qtable.pkl")

    try:
        agent.load_q_table(q_table_path)
        print("Loaded existing Q-Table.")
    except Exception:
        print("No existing Q-Table, starting fresh.")

    epsilon = 1.0
    epsilon_decay = 0.995
    epsilon_min = 0.05
    total_reward = 0

    for episode in range(20000):
        env.reset()
        state = env.get_state()
        steps = 0
        agent.epsilon = epsilon

        while True:
            action = agent.choose_action(state)
            reward = env.step(action)
            next_state = env.get_state()
            agent.update(state, action, reward, next_state)
            state = next_state
            steps += 1

            if reward == 100 or steps > 300:
                break

        if epsilon > epsilon_min:
            epsilon *= epsilon_decay

        if env.is_solved():
            total_reward += 1

        if episode % 500 == 0 and episode != 0:
            print(f"Episode {episode} | Solved: {total_reward} | Epsilon: {epsilon:.4f}")
            total_reward = 0

    agent.save_q_table(q_table_path)
    print("Q-Table saved!")
    print("Training session done!")


if __name__ == "__main__":
    main()

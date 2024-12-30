import numpy as np
from collections import defaultdict
import time

class QLearning:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, exploration_rate=0.1):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.computation_times = []

    def get_state(self, guard_pos, player_pos, walls):
        """Convert current game state to a hashable state representation"""
        visibility_radius = 5  # Guard can only see 5 tiles around
        relative_x = player_pos[0] - guard_pos[0]
        relative_y = player_pos[1] - guard_pos[1]
        
        # If player is within visibility radius, include their position
        if abs(relative_x) <= visibility_radius and abs(relative_y) <= visibility_radius:
            player_direction = (
                np.sign(relative_x),
                np.sign(relative_y)
            )
        else:
            player_direction = (0, 0)  # Player not visible

        # Include nearby walls in state
        nearby_walls = tuple(
            (x, y) for x, y in walls 
            if abs(x - guard_pos[0]) <= 2 and abs(y - guard_pos[1]) <= 2
        )

        return (guard_pos, player_direction, nearby_walls)

    def get_action(self, state):
        """Choose action using epsilon-greedy policy"""
        if np.random.random() < self.epsilon or not self.q_table[state]:
            return np.random.choice(['up', 'down', 'left', 'right'])
        
        return max(self.q_table[state].items(), key=lambda x: x[1])[0]

    def update(self, state, action, reward, next_state):
        """Update Q-value for state-action pair"""
        start_time = time.time()
        best_next_value = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0
        current_q = self.q_table[state][action]
        
        # Q-learning update formula
        self.q_table[state][action] = current_q + self.lr * (
            reward + self.gamma * best_next_value - current_q
        )
        end_time = time.time()
        self.computation_times.append(end_time - start_time)

    def get_reward(self, old_distance, new_distance, found_player=False):
        """Calculate reward based on whether guard got closer to player"""
        if found_player:
            return 10  # High reward for finding player
        elif new_distance < old_distance:
            return 1  # Reward for getting closer
        elif new_distance > old_distance:
            return -1  # Penalty for getting further
        return -0.1  # Small penalty for standing still

    def heuristic(self, guard_pos, player_pos):
        """Heuristic to guide guards towards the player"""
        return -self.manhattan_distance(guard_pos, player_pos)

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def print_efficiency_metrics(self):
        if self.computation_times:
            avg_time = sum(self.computation_times) / len(self.computation_times)
            print(f"Average Computation Time per Q-Learning Update: {avg_time:.6f} seconds")
        else:
            print("No computation times recorded.")

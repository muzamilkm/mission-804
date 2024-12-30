import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
from heapq import heappop, heappush
import time

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)
        self.computation_times = []

    def forward(self, x):
        start_time = time.time()
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        end_time = time.time()
        self.computation_times.append(end_time - start_time)
        return x

    def print_efficiency_metrics(self):
        if self.computation_times:
            avg_time = sum(self.computation_times) / len(self.computation_times)
            print(f"Average Computation Time per Forward Pass: {avg_time:.6f} seconds")
        else:
            print("No computation times recorded.")

class GuardEnv:
    def __init__(self, maze_size, walls, player_pos):
        self.maze_size = maze_size
        self.walls = walls
        self.player_pos = player_pos
        self.action_space = ['up', 'down', 'left', 'right']
        self.observation_space = (maze_size[0], maze_size[1], 2)  # Guard position and player direction

    def reset(self):
        self.guard_pos = (0, 0)
        return self._get_state()

    def step(self, action):
        new_pos = self._get_new_position(action)
        if self._is_valid_move(new_pos):
            self.guard_pos = new_pos
        reward = self._get_reward()
        done = self._is_done()
        return self._get_state(), reward, done, {}

    def _get_state(self):
        relative_x = self.player_pos[0] - self.guard_pos[0]
        relative_y = self.player_pos[1] - self.guard_pos[1]
        player_direction = (np.sign(relative_x), np.sign(relative_y))
        return (self.guard_pos, player_direction)

    def _get_new_position(self, action):
        x, y = self.guard_pos
        if action == 'up': y -= 1
        elif action == 'down': y += 1
        elif action == 'left': x -= 1
        elif action == 'right': x += 1
        return (x, y)

    def _is_valid_move(self, pos):
        x, y = pos
        return (0 <= x < self.maze_size[0] and 
                0 <= y < self.maze_size[1] and 
                (x, y) not in self.walls)

    def _get_reward(self):
        distance = self._manhattan_distance(self.guard_pos, self.player_pos)
        return -distance

    def _is_done(self):
        return self._manhattan_distance(self.guard_pos, self.player_pos) < 3

    def _manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class GuardAgent:
    def __init__(self, position, maze_size):
        self.position = position
        self.maze_size = maze_size
        self.update_timer = 0
        self.path_update_interval = 30
        self.personality = random.random()  # Add randomized personality trait
        self.error_rate = random.uniform(0.1, 0.3)  # Each guard has different error rate

    def find_path_to_player(self, start, target, walls):
        """A* pathfinding with intentional errors"""
        if start == target:
            return []

        # Randomly modify target position slightly to create variation
        if random.random() < self.error_rate:
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            target = (
                max(0, min(self.maze_size[0]-1, target[0] + offset_x)),
                max(0, min(self.maze_size[1]-1, target[1] + offset_y))
            )

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.manhattan_distance(start, target)}
        
        while open_set:
            _, current = heappop(open_set)
            
            if current == target:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                
                # Randomly skip some path points to create variation
                if len(path) > 3 and random.random() < self.error_rate:
                    return path[::2]  # Take every other point
                return path

            # Randomize neighbor checking order
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            if random.random() < self.personality:
                random.shuffle(directions)

            for dx, dy in directions:
                next_pos = (current[0] + dx, current[1] + dy)
                
                if (0 <= next_pos[0] < self.maze_size[0] and 
                    0 <= next_pos[1] < self.maze_size[1] and 
                    next_pos not in walls):
                    
                    # Add some random cost to create path variation
                    random_cost = random.uniform(0.8, 1.2) if random.random() < self.error_rate else 1.0
                    tentative_g = g_score[current] + random_cost
                    
                    if tentative_g < g_score.get(next_pos, float('inf')):
                        came_from[next_pos] = current
                        g_score[next_pos] = tentative_g
                        f_score = tentative_g + self.manhattan_distance(next_pos, target)
                        heappush(open_set, (f_score, next_pos))

        nearest_pos = self.find_nearest_reachable(start, target, walls)
        if nearest_pos != start:
            return self.find_path_to_player(start, nearest_pos, walls)
        return []

    def find_nearest_reachable(self, start, target, walls):
        """Find nearest reachable point with some randomness"""
        best_dist = float('inf')
        best_pos = start
        search_radius = random.randint(3, 7)  # Randomize search radius
        
        for dx in range(-search_radius, search_radius + 1):
            for dy in range(-search_radius, search_radius + 1):
                check_pos = (target[0] + dx, target[1] + dy)
                if (0 <= check_pos[0] < self.maze_size[0] and
                    0 <= check_pos[1] < self.maze_size[1] and
                    check_pos not in walls):
                    dist = self.manhattan_distance(check_pos, target)
                    # Add random factor to distance calculation
                    if random.random() < self.error_rate:
                        dist *= random.uniform(0.8, 1.2)
                    if dist < best_dist:
                        best_dist = dist
                        best_pos = check_pos
        
        return best_pos

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

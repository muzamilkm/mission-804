import pygame

class Metrics:
    def __init__(self):
        self.interceptions = 0
        self.total_distance = 0
        self.steps = 0
        self.start_time = None
        self.end_time = None

    def record_interception(self):
        self.interceptions += 1

    def record_distance(self, distance):
        self.total_distance += distance
        self.steps += 1

    def start_timer(self):
        self.start_time = pygame.time.get_ticks()

    def stop_timer(self):
        self.end_time = pygame.time.get_ticks()

    def get_average_distance(self):
        return self.total_distance / self.steps if self.steps > 0 else 0

    def get_time_taken(self):
        return (self.end_time - self.start_time) / 1000 if self.start_time and self.end_time else 0

    def print_metrics(self):
        print(f"Interception Rate: {self.interceptions}")
        print(f"Average Distance to Player: {self.get_average_distance():.2f} tiles")
        print(f"Time Taken to Capture Player: {self.get_time_taken():.2f} seconds")

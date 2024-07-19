import tkinter as tk
import random

# Define the game parameters
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
SEGMENT_SIZE = 20
SNAKE_SPEEDS = {'Easy': 150, 'Medium': 100, 'Hard': 50}
DIFFICULTY = 'Medium'  # Change this to 'Easy', 'Medium', or 'Hard'
OBSTACLE_COUNT = 5
SNAKE_HEAD_EMOJI = "🐍"  # Snake head emoji
SNAKE_BODY_EMOJI = "🟢"  # Green circle for snake body
APPLE_EMOJI = "🍎"       # Apple emoji
OBSTACLE_EMOJI = "🟥"    # Red square for obstacles
SPLASH_EMOJI = "💥"      # Splash emoji for teleport effect

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='black')
        self.canvas.pack()

        # Create header for score
        self.header = self.canvas.create_text(WINDOW_WIDTH // 2, 20, text="Score: 0", fill='white', font=('Arial', 20), tag='header')

        # Initialize game variables
        self.init_game()

        # Bind keyboard events
        self.root.bind("<KeyPress>", self.change_direction)

        # Start the game loop
        self.game_loop()

    def init_game(self):
        """Initialize or reset the game variables."""
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = 'Right'
        self.apple = self.create_apple()
        self.obstacles = self.create_obstacles()
        self.score = 0
        self.game_over_flag = False  # Track if the game is over

        # Create the snake, apple, and obstacles
        self.update_snake()
        self.update_apple()
        self.update_obstacles()

        # Remove any restart button if it exists
        self.canvas.delete('restart_button')

    def create_apple(self):
        """Create a new apple at a random position."""
        x = random.randint(0, (WINDOW_WIDTH - SEGMENT_SIZE) // SEGMENT_SIZE) * SEGMENT_SIZE
        y = random.randint(0, (WINDOW_HEIGHT - SEGMENT_SIZE) // SEGMENT_SIZE) * SEGMENT_SIZE
        return (x, y)

    def create_obstacles(self):
        """Create random obstacles in the game."""
        obstacles = []
        while len(obstacles) < OBSTACLE_COUNT:
            x = random.randint(0, (WINDOW_WIDTH - SEGMENT_SIZE) // SEGMENT_SIZE) * SEGMENT_SIZE
            y = random.randint(0, (WINDOW_HEIGHT - SEGMENT_SIZE) // SEGMENT_SIZE) * SEGMENT_SIZE
            if (x, y) not in self.snake and (x, y) != self.apple:
                obstacles.append((x, y))
        return obstacles

    def update_snake(self):
        """Draw the snake on the canvas."""
        self.canvas.delete("snake")
        for index, segment in enumerate(self.snake):
            if index == 0:
                self.canvas.create_text(segment[0] + SEGMENT_SIZE // 2, segment[1] + SEGMENT_SIZE // 2, text=SNAKE_HEAD_EMOJI, font=('Arial', SEGMENT_SIZE), fill='white', tag='snake')
            else:
                self.canvas.create_text(segment[0] + SEGMENT_SIZE // 2, segment[1] + SEGMENT_SIZE // 2, text=SNAKE_BODY_EMOJI, font=('Arial', SEGMENT_SIZE), fill='white', tag='snake')

    def update_apple(self):
        """Draw the apple on the canvas."""
        self.canvas.delete("apple")
        self.canvas.create_text(self.apple[0] + SEGMENT_SIZE // 2, self.apple[1] + SEGMENT_SIZE // 2, text=APPLE_EMOJI, font=('Arial', SEGMENT_SIZE), fill='red', tag='apple')

    def update_obstacles(self):
        """Draw the obstacles on the canvas."""
        self.canvas.delete("obstacle")
        for obs in self.obstacles:
            self.canvas.create_text(obs[0] + SEGMENT_SIZE // 2, obs[1] + SEGMENT_SIZE // 2, text=OBSTACLE_EMOJI, font=('Arial', SEGMENT_SIZE), fill='red', tag='obstacle')

    def splash_effect(self, obs):
        """Create a splash effect before moving the obstacle."""
        x, y = obs
        self.canvas.create_text(x + SEGMENT_SIZE // 2, y + SEGMENT_SIZE // 2, text=SPLASH_EMOJI, font=('Arial', SEGMENT_SIZE), fill='yellow', tag='splash')
        self.root.after(200, self.canvas.delete, "splash")

    def move_obstacles(self):
        """Move obstacles randomly with a splash effect and update their positions."""
        for obs in self.obstacles:
            self.splash_effect(obs)
        self.root.after(200, self.perform_obstacle_teleport)

    def perform_obstacle_teleport(self):
        """Teleport obstacles to new random positions."""
        new_obstacles = []
        while len(new_obstacles) < OBSTACLE_COUNT:
            x = random.randint(0, (WINDOW_WIDTH - SEGMENT_SIZE) // SEGMENT_SIZE) * SEGMENT_SIZE
            y = random.randint(0, (WINDOW_HEIGHT - SEGMENT_SIZE) // SEGMENT_SIZE) * SEGMENT_SIZE
            if (x, y) not in self.snake and (x, y) != self.apple:
                new_obstacles.append((x, y))
        self.obstacles = new_obstacles
        self.update_obstacles()
        # Schedule the next obstacle move
        self.root.after(3000, self.move_obstacles)

    def change_direction(self, event):
        """Change the direction of the snake based on keyboard input."""
        if self.game_over_flag:
            return

        new_direction = event.keysym
        if new_direction in ['Left', 'Right', 'Up', 'Down']:
            # Prevent the snake from moving in the opposite direction
            if (self.direction == 'Left' and new_direction != 'Right') or \
               (self.direction == 'Right' and new_direction != 'Left') or \
               (self.direction == 'Up' and new_direction != 'Down') or \
               (self.direction == 'Down' and new_direction != 'Up'):
                self.direction = new_direction

    def move_snake(self):
        """Move the snake in the current direction and check for collisions."""
        if self.game_over_flag:
            return

        head_x, head_y = self.snake[0]
        if self.direction == 'Left':
            head_x -= SEGMENT_SIZE
        elif self.direction == 'Right':
            head_x += SEGMENT_SIZE
        elif self.direction == 'Up':
            head_y -= SEGMENT_SIZE
        elif self.direction == 'Down':
            head_y += SEGMENT_SIZE

        # Check for collisions with walls or itself
        if head_x < 0 or head_x >= WINDOW_WIDTH or head_y < 0 or head_y >= WINDOW_HEIGHT or (head_x, head_y) in self.snake or (head_x, head_y) in self.obstacles:
            self.game_over()
            return

        # Check for collision with apple
        if (head_x, head_y) == self.apple:
            self.snake.insert(0, (head_x, head_y))
            self.score += 10
            self.update_score()
            self.apple = self.create_apple()
            self.update_apple()
            if len(self.snake) % 5 == 0:  # Add more obstacles every 5 apples eaten
                self.obstacles = self.create_obstacles()
                self.update_obstacles()
        else:
            self.snake.insert(0, (head_x, head_y))
            self.snake.pop()

        self.update_snake()

    def update_score(self):
        """Update the score display on the canvas."""
        self.canvas.itemconfig('header', text=f"Score: {self.score}")

    def game_over(self):
        """Display game over message and final score with a restart button."""
        self.game_over_flag = True
        self.canvas.delete("all")
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30, text=f"Game Over!\nScore: {self.score}", fill='white', font=('Arial', 24))
        
        # Create restart button
        self.restart_button = tk.Button(self.root, text="Restart", command=self.restart_game)
        self.restart_button.pack(pady=20)

    def restart_game(self):
        """Restart the game."""
        self.restart_button.pack_forget()  # Remove restart button
        self.init_game()
        self.game_loop()  # Restart game loop

    def game_loop(self):
        """Game loop to repeatedly move the snake and update the screen."""
        self.move_snake()
        self.root.after(SNAKE_SPEEDS[DIFFICULTY], self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    game.move_obstacles()  # Start moving obstacles
    root.mainloop()

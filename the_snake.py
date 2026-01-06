from __future__ import annotations

import random
from typing import List, Optional, Tuple

import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20

# How many cells we have in each direction.
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

BOARD_BACKGROUND_COLOR = (0, 0, 0)

SNAKE_COLOR = (0, 255, 0)
APPLE_COLOR = (255, 0, 0)

# Directions are defined as vectors.
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

FPS = 20  # game speed

pygame.init()

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    0,
    32,
)
pygame.display.set_caption('The Snake')

clock = pygame.time.Clock()


# --- Base class ---


class GameObject:
    """Base class for all game objects on the board."""

    def __init__(
        self,
        position: Optional[Tuple[int, int]] = None,
        body_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        """Initialize a game object.

        Parameters
        ----------
        position:
            Position of the object in pixels. If omitted, the object is placed
            in the centre of the screen.
        body_color:
            RGB color of the object.
        """
        if position is None:
            # Align to grid.
            pos_x = (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE
            pos_y = (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE
            position = (pos_x, pos_y)

        self.position: Tuple[int, int] = position
        self.body_color: Tuple[int, int, int] = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the object on the given surface.

        This method is intended to be overridden in child classes.
        """
        raise NotImplementedError


# --- Apple ---


class Apple(GameObject):
    """Apple that the snake can eat."""

    def __init__(self) -> None:
        """Create an apple in a random position."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self) -> None:
        """Move the apple to a random cell on the board."""
        grid_x = random.randint(0, GRID_WIDTH - 1)
        grid_y = random.randint(0, GRID_HEIGHT - 1)
        self.position = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the apple as a red square."""
        rect = pygame.Rect(
            self.position[0],
            self.position[1],
            GRID_SIZE,
            GRID_SIZE,
        )
        pygame.draw.rect(surface, self.body_color, rect)


# --- Snake ---


class Snake(GameObject):
    """The main character of the game — the snake."""

    def __init__(self) -> None:
        """Create a snake with length 1 in the centre of the field."""
        super().__init__(body_color=SNAKE_COLOR)
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.last: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """Return the position of the snake head."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Apply the buffered `next_direction` if it is valid."""
        if self.next_direction is None:
            return

        cur_dx, cur_dy = self.direction
        next_dx, next_dy = self.next_direction

        # Snake cannot instantly move in the opposite direction.
        if (cur_dx == -next_dx) and (cur_dy == -next_dy):
            return

        self.direction = self.next_direction
        self.next_direction = None

    def move(self) -> None:
        """Move the snake one cell in the current direction.

        Adds a new head to the list of positions and optionally removes
        the last element if the snake has not grown.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Check for self-collision (ignore head and neck).
        if new_head in self.positions[2:]:
            self.reset()
            return

        # Insert new head.
        self.positions.insert(0, new_head)

        # Remove tail if we haven't grown.
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the snake and erase its last segment if needed."""
        # Erase last segment.
        if self.last is not None:
            rect = pygame.Rect(
                self.last[0],
                self.last[1],
                GRID_SIZE,
                GRID_SIZE,
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, rect)

        # Draw all segments.
        for pos_x, pos_y in self.positions:
            rect = pygame.Rect(pos_x, pos_y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)

    def reset(self) -> None:
        """Reset the snake to its initial state after a collision."""
        pos_x = (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE
        pos_y = (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE
        centre = (pos_x, pos_y)

        self.length = 1
        self.positions = [centre]
        self.position = centre
        self.last = None
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None


# --- Helper functions ---


def handle_keys(snake: Snake) -> None:
    """Handle keyboard input and window events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT


# --- Main game loop ---


def main() -> None:
    """Run the Snake game."""
    screen.fill(BOARD_BACKGROUND_COLOR)

    snake = Snake()
    apple = Apple()

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        snake.draw(screen)
        apple.draw(screen)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()

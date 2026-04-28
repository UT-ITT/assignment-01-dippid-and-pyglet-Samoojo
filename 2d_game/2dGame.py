import pyglet
from pyglet import window, shapes
from DIPPID import SensorUDP
import time
import random
import math


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PORT = 5700
BODY_SIZE = 25
APPLE_SIZE = 10
SEGMENT_DISTANCE = 5
GAME_OVER_DURATION = 10

sensor = SensorUDP(PORT)

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

head = shapes.Circle(400, 400, BODY_SIZE, BODY_SIZE, (105, 155, 0))

# Apple Model
apple = shapes.Circle(200, 200, APPLE_SIZE, APPLE_SIZE, (200, 50, 0))
apple_stick = shapes.Line(200, 210, 200, 220, color=(101, 67, 33))
apple_leaf = shapes.Triangle(200, 220, 208, 228, 200, 228, color=(34, 139, 34))

# Score label
score_label = pyglet.text.Label(
    "Length: 1",
    font_name="Arial",
    font_size=16,
    x=WINDOW_WIDTH - 10,
    y=WINDOW_HEIGHT - 10,
    anchor_x="right",
    anchor_y="top",
    color=(255, 255, 255, 255),
)

# Game Over label
game_over_label = pyglet.text.Label(
    "GAME OVER",
    font_name="Arial",
    font_size=48,
    x=WINDOW_WIDTH // 2,
    y=WINDOW_HEIGHT // 2 + 20,
    anchor_x="center",
    anchor_y="center",
    color=(220, 30, 30, 255),
)
restart_label = pyglet.text.Label(
    "Restarting...",
    font_name="Arial",
    font_size=20,
    x=WINDOW_WIDTH // 2,
    y=WINDOW_HEIGHT // 2 - 35,
    anchor_x="center",
    anchor_y="center",
    color=(255, 255, 255, 200),
)

# Snake body colour pattern
BODY_COLORS = [
    (105, 155, 0),
    (80, 130, 0),
    (130, 180, 20),
    (60, 110, 0),
]

body_parts = []
history = []
body_length = 1

apple.x = random.randint(APPLE_SIZE + BODY_SIZE * 2, WINDOW_WIDTH - APPLE_SIZE)
apple.y = random.randint(APPLE_SIZE + BODY_SIZE * 2, WINDOW_HEIGHT - APPLE_SIZE)

# Game-over state
game_over = False
game_over_start = None


def get_head_direction():
    if len(history) >= 2:
        dx = history[0][0] - history[1][0]
        dy = history[0][1] - history[1][1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            return dx / dist, dy / dist
    return 1.0, 0.0  # default


def draw_snake_head():
    head.draw()

    dx, dy = get_head_direction()
    px, py = -dy, dx

    # Eyes:
    eye_offset = BODY_SIZE * 0.45
    eye_forward = BODY_SIZE * 0.35
    eye_radius = BODY_SIZE * 0.18
    pupil_radius = eye_radius * 0.55

    for side in (1, -1):
        ex = head.x + dx * eye_forward + px * side * eye_offset
        ey = head.y + dy * eye_forward + py * side * eye_offset
        eye_white = shapes.Circle(
            int(ex), int(ey), int(eye_radius), color=(240, 240, 240)
        )
        pupil = shapes.Circle(
            int(ex + dx * 2), int(ey + dy * 2), int(pupil_radius), color=(10, 10, 10)
        )
        eye_white.draw()
        pupil.draw()

    # Tongue:
    tongue_base_x = int(head.x + dx * BODY_SIZE)
    tongue_base_y = int(head.y + dy * BODY_SIZE)
    tongue_len = 14
    fork_len = 7
    fork_spread = 5

    tip_x = tongue_base_x + dx * tongue_len
    tip_y = tongue_base_y + dy * tongue_len

    tongue_line = shapes.Line(
        tongue_base_x,
        tongue_base_y,
        int(tip_x),
        int(tip_y),
        color=(200, 0, 50),
    )
    tongue_line.draw()

    for side in (1, -1):
        fx = tip_x + dx * fork_len + px * side * fork_spread
        fy = tip_y + dy * fork_len + py * side * fork_spread
        fork = shapes.Line(int(tip_x), int(tip_y), int(fx), int(fy), color=(200, 0, 50))
        fork.draw()


def draw_apple():
    apple.draw()
    # Stick:
    sx, sy = int(apple.x), int(apple.y + APPLE_SIZE)
    apple_stick.x = sx
    apple_stick.y = sy
    apple_stick.x2 = sx
    apple_stick.y2 = sy + 10
    apple_stick.draw()
    # Leaf:
    lx, ly = sx, sy + 10
    apple_leaf.x = lx
    apple_leaf.y = ly
    apple_leaf.x2 = lx + 8
    apple_leaf.y2 = ly + 8
    apple_leaf.x3 = lx
    apple_leaf.y3 = ly + 8
    apple_leaf.draw()


def reset_snake():
    global body_length, body_parts, history, game_over, game_over_start
    body_length = 1
    body_parts = []
    history = []
    game_over = False
    game_over_start = None
    head.x = 400
    head.y = 400


def moveSnake():
    win.clear()
    # The movement was based of demo_pyglet/pyglet_DIPPID.py
    if not sensor.get_capabilities() == []:
        if (
            sensor.get_value("gravity")["y"] > 1
            or sensor.get_value("gravity")["y"] < -1
        ):
            if head.y + sensor.get_value("gravity")["y"] + BODY_SIZE > WINDOW_HEIGHT:
                head.y = WINDOW_HEIGHT - BODY_SIZE
            elif head.y + sensor.get_value("gravity")["y"] - BODY_SIZE < 0:
                head.y = 0 + BODY_SIZE
            else:
                head.y += sensor.get_value("gravity")["y"]
        if (
            sensor.get_value("gravity")["x"] > 1
            or sensor.get_value("gravity")["x"] < -1
        ):
            if head.x + sensor.get_value("gravity")["x"] + BODY_SIZE > WINDOW_WIDTH:
                head.x = WINDOW_WIDTH - BODY_SIZE
            elif head.x + sensor.get_value("gravity")["x"] - BODY_SIZE < 0:
                head.x = 0 + BODY_SIZE
            else:
                head.x += sensor.get_value("gravity")["x"]

    draw_snake_head()

    # Track history
    if len(history) == 0:
        history.insert(0, (head.x, head.y))
    else:
        last_x, last_y = history[0]
        dist_moved = math.sqrt((head.x - last_x) ** 2 + (head.y - last_y) ** 2)
        if dist_moved > 5:
            history.insert(0, (head.x, head.y))

    max_history = body_length * SEGMENT_DISTANCE
    if len(history) > max_history:
        history.pop()

    # Draw body
    for i in range(len(body_parts)):
        index = (i + 1) * SEGMENT_DISTANCE
        if index < len(history):
            pos = history[index]
            body_parts[i].x = pos[0]
            body_parts[i].y = pos[1]
            body_parts[i].color = BODY_COLORS[i % len(BODY_COLORS)]
            body_parts[i].draw()


def repositionApple():
    for _ in range(1000):  # max attempts to avoid infinite loop
        x = random.randint(APPLE_SIZE, WINDOW_WIDTH - APPLE_SIZE)
        y = random.randint(APPLE_SIZE, WINDOW_HEIGHT - APPLE_SIZE)
        # Check against head
        if math.sqrt((x - head.x) ** 2 + (y - head.y) ** 2) < (BODY_SIZE + APPLE_SIZE):
            continue
        # Check against each body segment
        on_body = False
        for seg in body_parts:
            if math.sqrt((x - seg.x) ** 2 + (y - seg.y) ** 2) < (
                BODY_SIZE + APPLE_SIZE
            ):
                on_body = True
                break
        if not on_body:
            apple.x = x
            apple.y = y
            return


def eatApple():
    dx = head.x - apple.x
    dy = head.y - apple.y
    distance = math.sqrt(dx**2 + dy**2)

    if distance < (BODY_SIZE + APPLE_SIZE):
        global body_length
        color = BODY_COLORS[len(body_parts) % len(BODY_COLORS)]
        segment = shapes.Circle(400, 400, BODY_SIZE, color=color)
        body_parts.append(segment)
        body_length += 1
        repositionApple()


def checkSelfCollision():
    global game_over, game_over_start

    for i in range(2, len(body_parts)):
        segment = body_parts[i]
        dx = head.x - segment.x
        dy = head.y - segment.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < (BODY_SIZE * 1.5):
            if not game_over:
                game_over = True
                game_over_start = time.time()
            break


@win.event
def on_draw():
    global game_over, game_over_start

    currentTime = time.time()

    if game_over:
        win.clear()
        for i in range(len(body_parts)):
            index = (i + 1) * SEGMENT_DISTANCE
            if index < len(history):
                body_parts[i].draw()
        draw_snake_head()
        game_over_label.draw()
        restart_label.draw()

        elapsed = currentTime - game_over_start
        remaining = max(0, GAME_OVER_DURATION - elapsed)
        restart_label.text = f"Restarting in {int(remaining) + 1}s..."

        if elapsed >= GAME_OVER_DURATION:
            reset_snake()
        return

    moveSnake()
    draw_apple()
    eatApple()
    checkSelfCollision()

    score_label.text = f"Length: {body_length}"
    score_label.draw()


pyglet.app.run()

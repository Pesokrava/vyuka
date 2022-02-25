
import time
import tkinter
from random import choice, randint, random
from typing import Union, List
from itertools import cycle
from math import sqrt, hypot, floor, acos, asin, atan, cos, sin

# window settings
# ---------------------
WIDTH = 800
HEIGHT = 600
BACKGROUND = 'blue'
# ---------------------

# ball settings
# ---------------------
BALL_SHIFT = 1  # ball shift each frame
REFRESH = 2  # refresh rate 1000/REFRESH = FPS
No_BALLS = 2  # number of balls (with enabled collisions might start lagging due to the complexity of the problem)
RADII = 50  # radius of the balls can be either int (all balls same radius) or
# list [min, max] for random radiuses in range (not recommended weird things might happen)
BALL_COLORS = ['red', 'yellow', 'green', 'purple', 'pink', 'orange', 'salmon3', 'firebrick', 'purple4']
RANDOM_COLORS = False  # turns on random colors
OUTLINE_WIDTH = 1  # sets the thickness of the outline of the balls
COLLISIONS = True  # turns on/off the collisions between the balls, when turned off CPU will handle way more balls
PREVIOUS_COLLISIONS = set()  # tracks previous collisions, initially empty set
LIMIT = 1000  # limits the maximum balls to LIMIT (your PC might handle more)
if No_BALLS < 1:
    raise ValueError('Number of balls must be positive integer!')
if No_BALLS == 1:
    COLLISIONS = False
if COLLISIONS:
    LIMIT = 100  # limit with collisions enabled
# ---------------------
canvas = tkinter.Canvas(width=WIDTH, height=HEIGHT, background=BACKGROUND)
canvas.pack()


def generate_balls(no_balls: int=1, *,
                   limit: int=50,  # this limits the number of maximum balls to 50
                   screen_width: int=800,
                   screen_height: int=600,
                   radii: Union[int, List[int]] = 50,
                   colors: Union[str, List[str]] = 'red',
                   random_colors: bool = False,
                   line_width: int = 1) -> dict:
    if no_balls > limit:
        no_balls = limit
    balls = {}
    # sequential colors if random_colors is set to False, will cycle trough colors list
    if not random_colors and isinstance(colors, list):
        color_it = cycle(colors)


    for _ in range(no_balls):
        # random direction at the beginning
        x_dir = random()
        y_dir = sqrt(1-x_dir**2)
        info = {'direction': {'x': x_dir, 'y': y_dir}}

        # radius of the ball if it is list picks random number from the interval list[0], list[1]
        if isinstance(radii, list):
            info['radius'] = randint(radii[0], radii[1])
        else:
            info['radius'] = radii

        # random initial coordinates of each ball
        info['coords'] = {'x': randint(info['radius'], screen_width - info['radius']),
                          'y': randint(info['radius'], screen_height - info['radius'])}

        # if balls:
        #     while True:
        #         for Ball_id in balls.keys():
        #             if hypot(balls[Ball_id]['coords']['x'] - info['coords']['x'],
        #                      balls[Ball_id]['coords']['y'] - info['coords']['y']) <= balls[Ball_id]['radius'] + info['radius']:
        #                 info['coords'] = {'x': randint(info['radius'], screen_width - info['radius']),
        #                                   'y': randint(info['radius'], screen_height - info['radius'])}

        # color of the ball if it is list picks random color from the list
        if isinstance(colors, list):
            if random_colors:
                info['color'] = choice(colors)
            else:
                info['color'] = next(color_it)
        else:
            info['color'] = colors

        # get valid coordinates for drawing the circle e.g. [x,y] -> [x0,y0,x1,y1]
        coords = uncenter(info['coords']['x'], info['coords']['y'], info['radius'])
        # create circle and store its id in the ball_id variable
        ball_id = canvas.create_oval(coords[0], coords[1], coords[2], coords[3], fill=info['color'], width=line_width)
        # use ball_id as key for ball information
        balls[ball_id] = info

    return balls


def uncenter(x: int, y: int, radius) -> List[int]:
    return [x-radius,
            y-radius,
            x+radius,
            y+radius]


def center(corner_coords: list) -> List[int]:
    return [corner_coords[0] + abs(corner_coords[0]-corner_coords[2])//2,
            corner_coords[1] + abs(corner_coords[1]-corner_coords[3])//2]


def normalize_direction(direction: int):
    if direction >= 360:
        direction -= 360
    elif direction <= -180:
        direction += 180
    return direction


def check_wall_collision(ball_id, screen_width, screen_height) -> None:
    global BALLS
    ball = BALLS[ball_id]
    # left and right wall
    if ball['coords']['x'] - ball['radius'] <= 0 or ball['coords']['x'] + ball['radius'] >= screen_width:
        ball['direction']['x'] *= -1

    # top and bottom wall
    if ball['coords']['y'] - ball['radius'] <= 0 or ball['coords']['y'] + ball['radius'] >= screen_height:
        ball['direction']['y'] *= -1

    BALLS[ball_id] = ball


def rotate_coords(x, y, angle) -> dict:
    x_tr = x * cos(angle) - y * sin(angle)
    y_tr = x * sin(angle) + y * cos(angle)
    return {'x_tr': x_tr, 'y_tr': y_tr}


def inverse_rotate_coords(x_tr, y_tr, angle) -> dict:
    x = x_tr * cos(angle) + y_tr * sin(angle)
    y = -1 * x_tr * sin(angle) + y_tr * cos(angle)
    return {'x': x, 'y': y}


def direction_to_angle(dir_x, dir_y) -> float:
    return atan(dir_y / dir_x)


def check_ball_collision(ball_ids: tuple, previous_collisions: set) -> set:
    global BALLS, BALL_COLLISIONS_TOLERANCE, BALL_SHIFT

    for i, ball_id in enumerate(ball_ids[:-1]):
        for other_ball_id in ball_ids[i+1:]:
            if (ball_id, other_ball_id) in previous_collisions:
                continue
            ball, other_ball = BALLS[ball_id], BALLS[other_ball_id]

            relative_x = abs(ball['coords']['x'] - other_ball['coords']['x'])
            relative_y = abs(ball['coords']['y'] - other_ball['coords']['y'])
            center_distance = floor(hypot(relative_x, relative_y))
            radii_sum = ball['radius'] + other_ball['radius']

            if center_distance <= radii_sum:
                if relative_x < relative_y:
                    collision_angle = asin(relative_x/radii_sum)
                else:
                    collision_angle = acos(relative_y/radii_sum)

                rot_ball_dir = rotate_coords(ball['direction']['x'],
                                             ball['direction']['y'],
                                             collision_angle)
                rot_other_ball_dir = rotate_coords(other_ball['direction']['x'],
                                                   other_ball['direction']['y'],
                                                   collision_angle)
                rot_ball_dir['y_tr'] *= -1
                rot_other_ball_dir['y_tr'] *= -1
                inv_rot_ball_dir = inverse_rotate_coords(rot_ball_dir['x_tr'],
                                                         rot_ball_dir['y_tr'],
                                                         collision_angle)
                inv_rot_other_ball_dir = inverse_rotate_coords(rot_other_ball_dir['x_tr'],
                                                               rot_other_ball_dir['y_tr'],
                                                               collision_angle)

                ball['direction']['x'] = inv_rot_ball_dir['x']
                ball['direction']['y'] = inv_rot_ball_dir['y']
                other_ball['direction']['x'] = inv_rot_other_ball_dir['x']
                other_ball['direction']['y'] = inv_rot_other_ball_dir['y']

                previous_collisions.add((ball_id, other_ball_id))

                BALLS[ball_id] = ball
                BALLS[other_ball_id] = other_ball

    ids_to_delete = []
    for previous_collision_id in previous_collisions:
        center_distance = hypot(BALLS[previous_collision_id[0]]['coords']['x'] - BALLS[previous_collision_id[1]]['coords']['x'],
                                BALLS[previous_collision_id[0]]['coords']['y'] - BALLS[previous_collision_id[1]]['coords']['y']) - 30
        radii_sum = BALLS[previous_collision_id[0]]['radius'] + BALLS[previous_collision_id[1]]['radius']
        if center_distance > radii_sum:
            ids_to_delete.append(previous_collision_id)

    for Id in ids_to_delete:
        previous_collisions.discard(Id)
    return previous_collisions


def animation():
    global WIDTH, HEIGHT, BALLS, BALLS_IDS, REFRESH, COLLISIONS, PREVIOUS_COLLISIONS

    # for each ball do the animation and check for wall collisions and if ball collisions are enabled also for them
    # with enabled ball collisions and higher number of balls calculations will be very complex and animation might
    # start lagging
    if COLLISIONS:
        PREVIOUS_COLLISIONS = check_ball_collision(BALLS_IDS, PREVIOUS_COLLISIONS)

    for ball_id in BALLS.keys():
        ball = BALLS[ball_id]
        # checking the collisions and changing the directions if there is one
        check_wall_collision(ball_id, screen_width=WIDTH, screen_height=HEIGHT)
        # move the coordinates to new place
        # ball['coords']['x'] += round(BALL_SHIFT * ball['direction']['x'])
        # ball['coords']['y'] += round(BALL_SHIFT * ball['direction']['y'])
        ball['coords']['x'] += round(BALL_SHIFT * ball['direction']['x'], 1)
        ball['coords']['y'] += round(BALL_SHIFT * ball['direction']['y'], 1)
        # move the ball itself according to new coordinates
        canvas.coords(ball_id, uncenter(ball['coords']['x'], ball['coords']['y'], ball['radius']))
    canvas.after(REFRESH, animation)


if __name__ == '__main__':
    BALLS = generate_balls(No_BALLS, limit=LIMIT, radii=RADII, colors=BALL_COLORS, random_colors=RANDOM_COLORS,
                           screen_width=WIDTH, screen_height=HEIGHT, line_width=OUTLINE_WIDTH)
    BALLS_IDS = tuple(BALLS.keys())
    animation()
    canvas.mainloop()

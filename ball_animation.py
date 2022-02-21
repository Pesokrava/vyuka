import time
import tkinter
from random import choice, randint


WIDTH = 800
HEIGHT = 600
BACKGROUND = 'blue'
BALL_SIZE = 25
BALL_COLOR = 'red'
BALL_DIR = {'x': -1, 'y': 1}
BALL_SHIFT = 10
REFRESH = 10
INITIAL_COORDS = {'x': WIDTH//2, 'y': HEIGHT//2}
COUNT = 1

BALL_COLORS= ['red', 'blue', 'yellow', 'green', 'purple', 'pink']

canvas = tkinter.Canvas(width=WIDTH, height=HEIGHT, background=BACKGROUND)
canvas.pack()


def uncenter(x: int, y: int) -> list[int]:
    global BALL_SIZE
    return [x-BALL_SIZE//2,
            y-BALL_SIZE//2,
            x+BALL_SIZE//2,
            y+BALL_SIZE//2]


def center(corner_coords: list) -> list[int]:
    return [corner_coords[0] + abs(corner_coords[0]-corner_coords[2])//2,
            corner_coords[1] + abs(corner_coords[1]-corner_coords[3])//2]


def animation():
    global WIDTH, BALL_COLOR, coords, COUNT, BALL_SIZE
    coords = center(canvas.coords('BALL'))
    # x
    coords[0] += BALL_SHIFT*BALL_DIR['x']
    # y
    coords[1] += BALL_SHIFT*BALL_DIR['y']
    coords = uncenter(coords[0], coords[1])
    if coords[0] <= 0:
        BALL_DIR['x'] = 1


    if coords[1] <= 0:
        BALL_DIR['y'] = 1


    if coords[2] >= WIDTH:
        BALL_DIR['x'] = -1

    if coords[3] >= HEIGHT:
        BALL_DIR['y'] = -1

    canvas.delete('BALL')
    canvas.create_oval(coords[0], coords[1], coords[2], coords[3], fill=BALL_COLOR, tags='BALL')
    canvas.after(REFRESH, animation)


coords = uncenter(INITIAL_COORDS['x'], INITIAL_COORDS['y'])
canvas.create_oval(coords[0], coords[1], coords[2], coords[3], fill=BALL_COLOR, tags='BALL')
animation()
canvas.mainloop()

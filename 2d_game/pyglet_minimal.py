import pyglet
from pyglet import window, shapes

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

square = shapes.Rectangle(400, 400, 200, 200, (255, 0, 0))

@win.event
def on_draw():
    win.clear()
    square.draw()

pyglet.app.run()

import argparse
from py_overdrive_sdk.py_overdrive import Overdrive
from random import randint
# use pygle to have a friendly keyboard interface! It's a toy, after all ;-)
# adapted from https://gist.github.com/davepape/6715432
from pyglet.gl import *

# parse input
parser = argparse.ArgumentParser()
parser.add_argument("--car", help="id of the bluetooth car")
parser.add_argument("--host", help="host of the node gateway for bluetooth communication", default='127.0.0.1')
parser.add_argument("--port", help="port of the node gateway for bluetooth communication", type=int, default=8005)
args = parser.parse_args()

# init pyglet window with stylish image, size 240x400
window = pyglet.window.Window(240, 400)
image = pyglet.resource.image('pyglet_screen_savers/ff-family-{}.jpg'.format(randint(0, 3)))


"""
PYGLET WINDOW EVENTS
"""


@window.event
def on_draw():
    window.clear()
    image.blit(0, 0)


@window.event
def on_key_press(key, modifiers):
    if key == pyglet.window.key.UP:
        car.change_speed(800, 2000)
        print("---UP!")
    elif key == pyglet.window.key.DOWN:
        car.change_speed(400, 2000)
        print("---DOWN!")
    elif key == pyglet.window.key.RIGHT:
        car.change_lane_right(400, 2000)
        print("---RIGHT!")
    elif key == pyglet.window.key.LEFT:
        car.change_lane_left(400, 2000)
        print("---LEFT!")
    else:
        print("---EXIT!")
        pyglet.app.exit()
        return


"""
RUN THE MAIN LOOP
"""


print("Wait until window gets opened and then press any key to start!")
input()
# init car
print("Connecting to the car now...")
# use connected car as a context
with Overdrive(args.host, args.port, args.car, verbose=True) as connected_car:
    # start input loop
    pyglet.app.run()

# print goodbye and exit
print("Car disconnected!")

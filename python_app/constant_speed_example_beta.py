import argparse
from py_overdrive_sdk.py_overdrive import Overdrive

# parse input
parser = argparse.ArgumentParser()
parser.add_argument("--car", help="id of the bluetooth car")
parser.add_argument("--host", help="host of the node gateway for bluetooth communication", default='127.0.0.1')
parser.add_argument("--port", help="port of the node gateway for bluetooth communication", type=int, default=8005)
args = parser.parse_args()

# let's drive!
with Overdrive(args.host, args.port, args.car, verbose=True) as connected_car:  # init overdrive object
    connected_car.change_speed(400, 2000)  # set car speed with speed = 400, acceleration = 2000
    input()  # hold the program so it won't end abruptly

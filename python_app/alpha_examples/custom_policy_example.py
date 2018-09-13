import argparse
from py_overdrive_sdk.py_overdrive import Overdrive

# parse input
parser = argparse.ArgumentParser()
parser.add_argument("--car", help="id of the bluetooth car")
parser.add_argument("--host", help="host of the node gateway for bluetooth communication", default='127.0.0.1')
parser.add_argument("--port", help="port of the node gateway for bluetooth communication", type=int, default=8005)
args = parser.parse_args()


TOP_SPEED = 2000
BRAKE_SPEED = 1000


# define custom driving policy
def my_driving_policy(self, **kwargs):
    """
    Just an example of driving policy for the oval truck: if some condition is met, adjust speed

    :param kwargs will be a location event as dict produced by the 'build_location_event' function
    :return:
    """
    print(kwargs)
    # if the car is in the starting straight segments of the oval, set speed to 1000 if not already there
    if kwargs['piece'] in [34, 57] and kwargs['self_speed'] != TOP_SPEED:
        print('Ride baby!')
        self.change_speed(TOP_SPEED, 2000)
    # if the car is in the curving segments of the oval, set speed to 400 if not already there
    elif kwargs['piece'] in [39, 36] and kwargs['self_speed'] != BRAKE_SPEED:
        print('Slowing down!')
        self.change_speed(BRAKE_SPEED, 2000)
    else:
        return


# let's drive!
car = Overdrive(args.host, args.port, args.car, my_driving_policy)  # init overdrive object with custom policy
car.change_speed(400, 2000)  # set car speed with speed = 400, acceleration = 2000
# the car will change speed when traversing the starting straight segment
input()  # hold the program so it won't end abruptly

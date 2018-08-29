import argparse
from py_overdrive_sdk.py_overdrive import Overdrive

# parse input
parser = argparse.ArgumentParser()
parser.add_argument("--car", help="id of the bluetooth car")
parser.add_argument("--host", help="host of the node gateway for bluetooth communication", default='127.0.0.1')
parser.add_argument("--port", help="port of the node gateway for bluetooth communication", type=int, default=8005)
args = parser.parse_args()


# define custom driving policy
def my_lap_driving_policy(self, **kwargs):
    """
    Just an example of driving policy for the oval truck: approx measure how long it takes to complete a lap

    :param kwargs will be a location event as dict produced by the 'build_location_event' function
    :return:
    """
    current_piece = kwargs['piece']
    if current_piece == 33:
        current_time = kwargs['notification_time']
        # time the lap and print it: if there is no last time, it means it's the first time
        if hasattr(self, 'last_starting_line_event'):
            time_lap = (current_time - self.last_starting_line_event).total_seconds()
            print('time lap in seconds was {}'.format(time_lap))
        # update lap time
        self.last_starting_line_event = current_time

    return


# let's drive!
car = Overdrive(args.host, args.port, args.car, my_lap_driving_policy)  # init overdrive object with custom policy
car.change_speed(800, 2000)  # set car speed with speed = 400, acceleration = 2000
input()  # hold the program so it won't end abruptly

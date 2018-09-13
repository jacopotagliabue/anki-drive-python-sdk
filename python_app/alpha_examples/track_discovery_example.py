"""
    Basic and NON-general example of a track discovery policy: the car will collect all piece IDs from the track
    and store them in a text file.

    If you then run 'create_track_image.py' a png image of the map will be produced.
"""

import argparse
from py_overdrive_sdk.py_overdrive import Overdrive

# parse input
parser = argparse.ArgumentParser()
parser.add_argument("--car", help="id of the bluetooth car")
parser.add_argument("--host", help="host of the node gateway for bluetooth communication", default='127.0.0.1')
parser.add_argument("--port", help="port of the node gateway for bluetooth communication", type=int, default=8005)
args = parser.parse_args()

# name of the output file
TRACK_FILE = 'track_piece_list.txt'


# define custom driving policy for track discovery
def discovery_driving_policy(self, **kwargs):
    """
    Just an example of policy keeping track of all the piece IDs in the track

    :param kwargs will be a location event as dict produced by the 'build_location_event' function
    :return:
    """
    current_piece = kwargs['piece']
    print('piece id: {}'.format(current_piece))
    # create a variable to store pieces if is not there
    if not hasattr(self, 'track_pieces'):
        self.track_pieces = []
    # first, ignore the start piece which has no image attached
    if current_piece == 33:
        return
    # then, always start from the finish line
    if current_piece != 34 and not self.track_pieces:
        return
    # if it's a new id, add it
    if current_piece not in self.track_pieces:
        self.track_pieces.append(kwargs['piece'])
        print('Added piece {}'.format(current_piece))
    # if id is there AND it is not the last one added (as we may have more consecutive location events
    # for the same id), we already map everything once - so quit
    else:
        if current_piece != self.track_pieces[-1]:
            with open(TRACK_FILE, 'w') as track_f:
                for p in self.track_pieces:
                    track_f.write('{}\n'.format(p))
            print('Stopping now!')
            car.change_speed(0, 1000)

    return


# let's drive!
car = Overdrive(args.host, args.port, args.car, discovery_driving_policy)  # init overdrive object with custom policy
car.change_speed(400, 2000)  # set car speed with speed = 400, acceleration = 2000
# the car will change speed when traversing the starting straight segment
input()  # hold the program so it won't end abruptly

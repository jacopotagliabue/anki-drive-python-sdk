"""
    Python wrapper for Anki Overdrive vehicle communication through a node gateway.
    This code has been developed with educational and R&D purposes for the 'Self-driving (very small) cars'
    blog series,

    The code is released under the Apache License 2.0:  FOR FULL LICENSE AND MORE INFO, PLEASE SEE README
"""

import struct
import threading
import socket
import time
from datetime import datetime
from queue import Queue, Empty


class Overdrive:

    def __init__(self, host, port, uuid, driving_policy=None, verbose=False):
        """

        :param host: socket host
        :param port: socket port
        :param uuid: uuid of the target blueetooth vehicle
        :param driving_policy: optional function supplied by the user to take action based on location events
        """
        # init node socket
        self.node_socket = socket.socket()
        self.node_socket.connect((host, port))
        # set some class variables
        self.uuid = uuid
        self._connected = False
        # store queues
        self._queues = {
            'commands': Queue(),  # queue to write commands to the gateway
            'locations': Queue()  # queue to write location events received from the gateway
        }
        self._threads = []
        # driving policy supplied by the user overwrite the standard one in _standard_driving_policy
        self._driving_policy = driving_policy
        # init current speed at 0
        self._speed = 0
        # set verbose to know how much to print (debug friendly=True)
        self._verbose = verbose
        # finally try to connect to the car through node socket
        self._connect(self.uuid)
        return

    def __del__(self):
        self._connected = False
        self._disconnect(self.uuid)

    """
        CONNECTION FUNCTIONS
    """

    def _disconnect(self, uuid):
        self.node_socket.send("DISCONNECT|{}\n".format(uuid).encode())

    def _connect(self, uuid):
        self._send_connect_message_to_socket(uuid)
        self._connected = True
        # fork thread to read and write to the bluetooth socket
        self._start_thread(self._send_thread)
        self._start_thread(self._read_thread)
        self._start_thread(self._location_changed_thread)
        self.turn_on_sdk_mode()
        # give it some time - this is fairly horrible but it's the startup of the process
        # so waiting a bit doesn't hurt anybody ;-)
        time.sleep(1)

    def _send_connect_message_to_socket(self, uuid):
        self.node_socket.send("CONNECT|{}\n".format(uuid).encode())
        # give it some time - this is fairly horrible but it's the startup of the process
        # so waiting a bit doesn't hurt anybody ;-)
        time.sleep(1)
        return

    """
        THREADING FUNCTIONS
    """

    def _start_thread(self, target_function):
        new_thread = threading.Thread(target=target_function)
        self._threads.append(new_thread)
        new_thread.start()

    def _read_thread(self):
        while self._connected:
            data = self.node_socket.recv(1024).decode()
            if data:
                b_data = bytes.fromhex(data)
                command_id = hex(struct.unpack_from("B", b_data, 1)[0])
                self._handle_notification(command_id, b_data)

    def _send_thread(self):
        while self._connected:
            try:
                data = self._queues['commands'].get_nowait()
                self.node_socket.send('{}\n'.format(data.hex()).encode())
            except Empty as empty_ex:
                continue
            except Exception as ex:
                raise ex

    def _location_changed_thread(self):
        while self._connected:
            try:
                (location, piece, offset, speed, clockwise, notification_time) = self._queues['locations'].get_nowait()
                location_event = self.build_location_event(location, piece, offset, speed, clockwise, notification_time)
                if self._driving_policy:
                    self._driving_policy(self, **location_event)
                else:
                    self._standard_driving_policy(**location_event)
            except Empty as empty_ex:
                continue
            except Exception as ex:
                raise ex

    def _handle_notification(self, command_id, data):
        # location notification
        if command_id == '0x27':
            # parse location
            location, piece, offset, speed, clockwise = struct.unpack_from("<BBfHB", data, 2)
            self._queues['locations'].put((location, piece, offset, speed, clockwise, datetime.utcnow()))
        # transition notification
        elif command_id == '0x29':
            # piece, piecePrev, offset, direction = struct.unpack_from("<BBfB", data, 2)
            # we could only get stuff like 0 0 65.69200134277344 255, puzzled for now on the meaning of
            # the data
            return
        else:
            # still not sure what are these ;-)
            if self._verbose:
                print('Unrecognized command id from notification {}'.format(command_id))

        return

    def _standard_driving_policy(self, **kwargs):
        """
        Just a placeholder driving policy for the oval truck: print out notifications

        :param data: tuple from location updates (location, piece, offset, speed, clockwise, datetime.utcnow())
        :return:
        """
        print(kwargs)
        return

    """
        UTILS FUNCTIONS
    """

    def build_location_event(self, location, piece, offset, speed, clockwise, notification_time):
        return {
            'location': location,
            'piece': piece,
            'offset': offset,
            'speed': speed,  # speed as notified from event
            'self_speed': self._speed,  # speed as internally stored
            'clockwise': clockwise,
            'notification_time': notification_time,
            'is_clockwise': hex(clockwise) == '0x47'  # '0x47' is the code for clockwise=True
        }

    def send_command(self, command):
        final_command = struct.pack("B", len(command)) + command
        self._queues['commands'].put(final_command)

    """
        COMMANDS TO DRIVE THE VEHICLE, CALLABLE FROM OUTSIDE
    """

    def change_speed(self, speed, accel):
        """

        :param speed: int mm/sec
        :param accel: int mm/sec^2
        :return:
        """
        command = struct.pack("<BHHB", 0x24, speed, accel, 0x01)
        # update current speed
        self._speed = speed
        self.send_command(command)

    def change_lane_right(self, speed, accel):
        """
        Wrapper around the change lane command to move right

        :param speed: int mm/sec
        :param accel: int mm/sec^2
        :return:
        """
        self.change_lane(speed, accel, 44.5)

    def change_lane_left(self, speed, accel):
        """
        Wrapper around the change lane command to move left

        :param speed: int mm/sec
        :param accel: int mm/sec^2
        :return:
        """
        self.change_lane(speed, accel, -44.5)

    def change_lane(self, speed, accel, offset):
        """

        :param speed: int mm/sec
        :param accel: int mm/sec^2
        :param offset: float (negative for left, positive for right)
        :return:
        """
        command = struct.pack("<BHHf", 0x25, speed, accel, offset)
        self.send_command(command)

    def turn_on_sdk_mode(self):
        self.send_command(b"\x90\x01\x01")



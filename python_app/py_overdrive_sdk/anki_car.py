from abc import ABC, abstractmethod
from py_overdrive_sdk.py_overdrive import Overdrive


class AnkiCar(ABC):

    def __init__(self, host, port, uuid, driving_policy, verbose):
        self.uuid = uuid
        self.overdrive_client = Overdrive(host, port, uuid, driving_policy, verbose)

    def __enter__(self):
        self.overdrive_client.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.overdrive_client.disconnect()
        return

    def __del__(self):
        self.overdrive_client.disconnect()
        return

    @abstractmethod
    def change_speed(self, speed, accel):
        pass

    @abstractmethod
    def change_lane_right(self, speed, accel):
        pass

    @abstractmethod
    def change_lane_left(self, speed, accel):
        pass

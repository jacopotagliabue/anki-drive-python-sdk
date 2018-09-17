from py_overdrive_sdk.anki_car import AnkiCar


class AnkiCharger(AnkiCar):

    def __init__(self, host, port, uuid, driving_policy=None, verbose=False):
        super().__init__(host, port, uuid, driving_policy, verbose)

        return

    def change_speed(self, speed, accel):
        self.overdrive_client.change_speed(speed, accel)

    def change_lane_right(self, speed, accel):
        self.overdrive_client.change_lane_right(speed, accel)

    def change_lane_left(self, speed, accel):
        self.overdrive_client.change_lane_left(speed, accel)

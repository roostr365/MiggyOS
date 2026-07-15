from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
import time
class LocomotionDriver:

    def __init__(self, client):
        self.client = client

    def stop(self):
        self.client.Move(0, 0, 0)

    def move_dist_sleep(self, dist, speed):
        self.client.Move(speed, 0, 0)
        time.sleep(dist/speed)
        self.stop()

    def rotate_radians_sleep(self, angle, speed):
        self.client.Move(0, 0, speed)
        time.sleep(angle/speed)
        self.stop()
    
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
import time

class LocomotionDriver:

    def __init__(self, client):
        self.client = client

    def stop(self):
        self.client.Move(0, 0, 0)

    def move_dist_sleep(self, dist, speed):
        if speed == 0:
            print("Movement canceled.")
            return
        self.client.Move(speed, 0, 0, True)
        time.sleep(abs(dist/speed))
        self.stop()

    def rotate_radians_sleep(self, angle, speed):
        if speed == 0:
            print("Movement canceled.")
            return
        self.client.Move(0, 0, speed, True)
        time.sleep(abs(angle/speed))
        self.stop()

    def move_and_rotate(self, move_speed, rotate_speed, move_dist, rotate_angle):
        if move_speed == 0 or rotate_speed == 0:
            print("Movement canceled.")
            return
        self.client.Move(move_speed, 0, rotate_speed, True)
        # Wait for both translation and rotation to complete
        duration = max(abs(move_dist / move_speed), abs(rotate_angle / rotate_speed))
        time.sleep(duration)
        self.stop()

    def stand(self):
        self.client.Squat2StandUp()
        time.sleep(5)

    def sit(self):
        self.client.StandUp2Squat()
        time.sleep(5)

    def damp(self):
        self.client.Damp()



 

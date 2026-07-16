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
    
 

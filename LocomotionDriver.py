from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
import time

class LocomotionDriver:

	def __init__(self, client):
		self.client = client

	def stop(self):
		self.client.Move(0, 0, 0)

	def move_dist_sleep(self, dist, speed):
		if speed == 0 or dist == 0:
			print("Movement canceled.")
			return
		# Direction comes from the sign of dist (+ forward, - backward)
		velocity = abs(speed) if dist > 0 else -abs(speed)
		self.client.Move(velocity, 0, 0, True)
		time.sleep(abs(dist / speed))
		self.stop()

	def rotate_radians_sleep(self, angle, speed):
		if speed == 0 or angle == 0:
			print("Movement canceled.")
			return
		# Direction comes from the sign of angle (+ counterclockwise, - clockwise)
		omega = abs(speed) if angle > 0 else -abs(speed)
		self.client.Move(0, 0, omega, True)
		time.sleep(abs(angle / speed))
		self.stop()

	def move_and_rotate(self, move_dist, rotate_angle, move_speed, rotate_speed):
		if move_speed == 0 or rotate_speed == 0:
			print("Movement canceled.")
			return
		velocity = abs(move_speed) if move_dist >= 0 else -abs(move_speed)
		omega = abs(rotate_speed) if rotate_angle >= 0 else -abs(rotate_speed)
		self.client.Move(velocity, 0, omega, True)
		time.sleep(abs(move_dist / move_speed))
		self.stop()

	def stand(self):
		self.client.Squat2StandUp()
		time.sleep(5)

	def sit(self):
	
		self.client.StandUp2Squat()
		time.sleep(5)

	def damp(self):
		self.client.Damp()


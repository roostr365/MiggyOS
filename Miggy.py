from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from LocomotionDriver import LocomotionDriver

class Miggy:
	def __init__(self, interface):
		ChannelFactoryInitialize(0, interface)
		print("Connected Succesfully!")
		self.client = LocoClient()
		self.client.SetTimeout(10.0)
		self.client.Init()

		self.locomotion = LocomotionDriver(self.client)

	def move_dist(self, distance, speed):
		self.locomotion.move_dist_sleep(distance, speed)

	def rotate_angle(self, angle, speed):
		self.locomotion.rotate_radians_sleep(angle, speed)

	def stop(self):
		self.locomotion.stop()
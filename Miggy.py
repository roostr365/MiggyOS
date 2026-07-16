from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from LocomotionDriver import LocomotionDriver
from ArmDriver import ArmDriver
from AudioDriver import AudioDriver

class Miggy:
	def __init__(self, interface):
		ChannelFactoryInitialize(0, interface)
		print("Connected Succesfully!")
		self.loco_client = LocoClient()
		self.loco_client.SetTimeout(10.0)
		self.loco_client.Init()

		self.arm_client = G1ArmActionClient()
		self.arm_client.SetTimeout(10.0)
		self.arm_client.Init()

		self.audio_client = AudioClient()
		self.audio_client.SetTimeout(10.0)
		self.audio_client.Init()

		self.locomotion = LocomotionDriver(self.loco_client)
		self.arm = ArmDriver(self.arm_client)
		self.audio = AudioDriver(self.audio_client)


	def move_dist(self, distance, speed):
		self.locomotion.move_dist_sleep(distance, speed)

	def rotate_angle(self, angle, speed):
		self.locomotion.rotate_radians_sleep(angle, speed)

	def stop(self):
		self.locomotion.stop()

	def rotate_and_move(self, move_speed, rotate_speed, distance, angle):
		self.locomotion.move_and_rotate(move_speed, rotate_speed, distance, angle)

	def sit(self):
		self.locomotion.sit()
		#self.locomotion.damp()

	def stand(self):
		self.locomotion.stand()

	def release_arm(self):
		self.arm.release()

	def run_special(self, str):
		try:
			self.arm.special(str)
		except Exception as e:
			print(str(e) + " given string not one of the special commands")

	def say(self, string, language):
		self.audio.say(string, {"english": 1, "chinese": 0}[language]) if language in ["chinese", "english"] else None

	def check_audio(self):
		return self.audio.get_latest_message()

	def clear_audio(self):
		self.audio.clear()
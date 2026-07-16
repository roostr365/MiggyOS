from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.core.channel import ChannelSubscriber

class AudioDriver:
    def __init__(self, client: AudioClient):
        self.client = client

        audio_msg_subscriber = ChannelSubscriber("rt/audio_msg", String_)
        audio_msg_subscriber.Init(self.hear, 10)

    def say(self, str):
        self.client.TtsMaker(str, 0)

    def hear(self, msg: String_):
        return msg.data
    
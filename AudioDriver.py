from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.core.channel import ChannelSubscriber

class AudioDriver:
    def __init__(self, client: AudioClient):
        self.client = client
        self.latest_message = None

        self.audio_msg_subscriber = ChannelSubscriber("rt/audio_msg", String_)
        self.audio_msg_subscriber.Init(self._callback, 10)

    def say(self, str, lang:int):
        self.client.TtsMaker(str, lang)

    def _callback(self, msg: String_):
        self.latest_message = msg.data
        print(self.latest_message)

    def get_latest_message(self):
        message = self.latest_message
        self.latest_message = None
        return message

    def clear(self):
        self.latest_message = None


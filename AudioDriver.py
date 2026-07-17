from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.core.channel import ChannelSubscriber
import json

class AudioDriver:
    def __init__(self, client: AudioClient):
        self.client = client
        self.latest_message = None

        self.audio_msg_subscriber = ChannelSubscriber("rt/audio_msg", String_)
        self.audio_msg_subscriber.Init(self._callback, 10)

    def say(self, text, lang: int):
        self.client.TtsMaker(text, lang)

    def _callback(self, msg: String_):
        self.latest_message = msg.data
        #print(self.latest_message)

    def get_latest_message(self):
        """Retrieve the latest audio message text, if available."""
        if not self.latest_message:
            return None
        try:
            data = json.loads(self.latest_message)
            message = data.get("text")
            self.latest_message = None
            return message
        except Exception:
            self.latest_message = None
            return None

    def clear(self):
        self.latest_message = None


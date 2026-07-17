from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.core.channel import ChannelSubscriber
import json

class AudioDriver:
    def __init__(self, client: AudioClient):
        self.client = client
        self.latest_message = None  # will hold the parsed text or None

        self.audio_msg_subscriber = ChannelSubscriber("rt/audio_msg", String_)
        self.audio_msg_subscriber.Init(self._callback, 10)

    def say(self, str, lang:int):
        self.client.TtsMaker(str, lang)

    def _callback(self, msg: String_):
        # msg.data is a string; try to parse JSON expecting {"text": "..."}
        raw = msg.data
        try:
            parsed = json.loads(raw)
            self.latest_message = parsed.get("text", raw)
        except Exception:
            # fallback: treat raw string as the transcript
            self.latest_message = raw
        print(f"[Audio] {self.latest_message}")

    def get_latest_message(self):
        if self.latest_message is None:
            return None
        msg = self.latest_message
        self.latest_message = None
        return msg

    def clear(self):
        self.latest_message = None

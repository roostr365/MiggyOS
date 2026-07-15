from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber

# The message type depends on the topic
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_

class StateDriver:

    def __init__(self):
        # Subscribe to robot state topic
        self.subscriber = ChannelSubscriber(
            "rt/sportmodestate",
            SportModeState_
        )

        self.subscriber.Init()

    def get_state(self):
        return self.subscriber.Read()
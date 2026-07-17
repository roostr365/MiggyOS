from unitree_sdk2py.g1.arm.g1_arm_action_client import action_map

class ArmDriver:

    def __init__(self, client):
        self.client = client

    def release(self):
        self.client.ExecuteAction(action_map.get("release arm"))

    def special(self, command_str):
        action = action_map.get(command_str)
        if action is None:
            raise ValueError(f"Invalid special command: {command_str}")
        self.client.ExecuteAction(action)
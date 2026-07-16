from openai import OpenAI, api_key
from Miggy import Miggy
import math
import time

preprompt = """
You control a Unitree G1 robot through the MiggyOS Python API.

Available commands:

miggy.move_dist(distance: float, speed: float)
- distance: meters. Positive = forward, negative = backward.
- speed: meters per second. negative means backwards. Negative SPEED!

miggy.rotate_angle(angle: float, speed: float)
- angle: radians. Positive = counterclockwise, negative = clockwise.
- speed: radians per second.
- Positive speed! value makes the robot turn left, negative speed value makes the robot turn right. 

Available libraries already imported:
import math
import time

Your output will be directly executed using Python exec().

Rules:
1. Output ONLY valid Python code.
2. Do not use markdown.
3. Do not include explanations or comments.
4. Do not create new classes or functions.
5. Only use miggy.move_dist(), miggy.rotate(), math, and time.sleep().
6. If multiple actions are needed, separate statements with semicolons.
7. Convert degrees to radians using math.radians().
8. Never output anything except executable Python.
9. You are using an instance of miggy called miggy. Adress all calls to instance miggy. Never capitalize.
10. Use time.sleep of appropriate length between each action
11. MAKE SURE TO ONLY USE THE COMMANDS GIVEN, DOUBLE CHECK THAT THEY MATCH THE GIVEN MIGGY COMMANDS

Examples:

User: Walk forward 2 meters
Output:
miggy.move_dist(2.0,0.5)

User: Turn right 90 degrees then walk 1 meter
Output:
Miggy.rotate(math.radians(-90),1.0); Miggy.move_dist(1.0,0.5)

"""

class AIMiggy:

    def __init__(self):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key="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"
        )

    def askAIMiggy(self, query):
        response = self.client.responses.create(
            model="openai/gpt-oss-120b",
            input=preprompt + query,
            max_output_tokens=4096,
            top_p=1,
            temperature=1,
            stream=False
        )

        return response

    def run(self, query, miggy):
        code = self.askAIMiggy(query).output_text
        print(code)
        try:
            input("code about to be executed: " + code + " Enter to accept") 
            exec(code)
        except Exception as e:
            print(str(e) + " Please try again.")


#aim = AIMiggy()
#aim.run("Please walk forward 2 meters and turn around")


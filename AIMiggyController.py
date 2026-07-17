from openai import OpenAI, api_key
from Miggy import Miggy
import math
import time

preprompt = """
You are an autonomous controller for a Unitree G1 robot using the MiggyOS Python API.

API

miggy.move_dist(distance: float, speed: float)
    distance: meters (+ forward, - backward)
    speed: meters/second (+ forward, - backward)

miggy.rotate_angle(angle: float, speed: float)
    angle: radians (+ counterclockwise, - clockwise)
    speed: radians/second (+ left, - right)
    
miggy.run_special(str: string)
    str: string that is used by the python sdk to find the high level command to move the arm. Can only be exactly these options:
    shake hand
    high five
    hug
    high wave
    clap
    face wave
    left kiss
    heart
    right heart
    hands up 
    x-ray
    right hand up
    reject
    right kiss
    two-hand kiss
    #End of list 
    Give the action time to complete.
    
miggy.release_arm()
    After using a special arm action, this function moves the arm back to a neutral position. 

Available modules:
- math
- time

Execution

Your response is executed directly with Python exec().

Requirements

- Output only executable Python.
- Do not use markdown, comments, or explanations.
- Do not define functions or classes.
- Only use the documented API, math, and time.sleep().
- Call methods only on the existing instance `miggy`.
- Use math.radians() whenever the user specifies degrees.
- Insert an appropriate time.sleep() between sequential robot actions.
- Verify every API call matches the documented method names and signatures exactly.
- Never output anything except Python code.

Examples

User: Walk forward 2 meters
miggy.move_dist(2.0, 0.5)

User: Turn right 90 degrees then walk 1 meter
miggy.rotate_angle(math.radians(-90), -1.0); time.sleep(...); miggy.move_dist(1.0, 0.5)
"""

class AIMiggy:

    def __init__(self):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key="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"
        )
        
        self.mode = 0

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


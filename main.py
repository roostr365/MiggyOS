print("Loading MiggyOS TM Copyright 2026 All Rights Reserved by The Miggy...")

import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from Miggy import Miggy

ChannelFactoryInitialize(0, sys.argv[1])
print("Connected Succesfully!")

miggy = Miggy()
commands = {"quit": "Quit the MiggyOS", "move": "Move the robot forward", "rotate": "Rotate the robot"}
running = True

def list_commands():
    for cmd in commands:
        print(cmd)
        print(commands[cmd])

running = True
while running:
    list_commands()
    command = input("Enter command: ")

    if command == "quit":
        running = False


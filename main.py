print("Loading MiggyOS TM Copyright 2026 All Rights Reserved by The Miggy...")

import sys
from Miggy import Miggy

miggy = Miggy(sys.argv[1])
commands = {"quit": "Quit the MiggyOS", "move": "Move the robot forward", "rotate": "Rotate the robot"}

def list_commands():
    for cmd in commands:
        print(cmd)
        print(commands[cmd])

running = True
try:
    while running:
        list_commands()
        command = input("Enter command: ")

        if command == "quit":
            miggy.stop()
        elif command == "move":
            distance = float(input("Enter distance: "))
            speed = float(input("Enter speed: "))
            miggy.move(distance, speed)
except KeyboardInterrupt:
    miggy.stop()




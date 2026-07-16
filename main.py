print("Loading MiggyOS TM Copyright 2026 All Rights Reserved by The Miggy...")

import sys
from Miggy import Miggy

try:
    miggy = Miggy(sys.argv[1])
except Exception as e:
    print("Failed to connect to the Miggy!!! " + str(e))
    sys.exit(1)
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
            miggy.move_dist(distance, speed)
        elif command == "rotate":
            angle = float(input("Enter angle: "))
            speed = float(input("Enter speed: "))
            miggy.rotate_angle(angle, speed)
        elif command == "mar":
            move_speed = float(input("Enter move speed: "))
            rotate_speed = float(input("Enter rotate speed: "))
            move_dist = float(input("Enter distance: "))
            rotate_angle = float(input("Enter angle: "))
            miggy.rotate_and_move(move_speed, rotate_speed, move_dist, rotate_angle)
except KeyboardInterrupt:
    miggy.stop()
    print("Exiting... Thanks for using MiggyOS!")




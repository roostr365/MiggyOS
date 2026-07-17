from Miggy import Miggy
from AIMiggyController import AIMiggy

import time

class TerminalInterface:

    @staticmethod
    def main(miggy, aimiggy):
        commands = {
            "quit": "Quit the MiggyOS",
            "move": "Move the robot forward",
            "rotate": "Rotate the robot",
            "mar": "Move the robot and rotate the robot",
            "sit": "Sit the robot down",
            "stand": "Stand the robot up",
            "audio": "Listen for a command and give to AI",
            "say": "Make the robot speak a phrase",
            "custom": "Use AI to run the robot DANGEROUS WARNING MAY CAUSE ARMAGEDDON AND THE RESURRECTION OF THE TERMINATOR AND ERASURE OF THE HUMAN RACE. USE WITH EXTREME CAUTION. Thanks for using MiggyOS!"
        }

        running = True

        def list_commands():
            for cmd in commands:
                print(cmd)
                print(commands[cmd])

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
                elif command == "custom":
                    query = input("Enter query for AI: ")
                    aimiggy.run(query, miggy)
                elif command == "audio":
                    miggy.clear_audio()
                    command = miggy.check_audio()
                    while command == None:
                        time.sleep(1)
                        command = miggy.check_audio()
                    aimiggy.run(command, miggy)
                elif command == "say":
                    lang = input("Input lanugage (english / chinese): ")
                    text = input("Input message: ")
                    miggy.say(text, lang)

        except KeyboardInterrupt:
            miggy.stop()
            print("Exiting... Thanks for using MiggyOS!")

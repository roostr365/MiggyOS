from Miggy import Miggy
from AIMiggyController import AIMiggy
import time

class AudioInterface:
    @staticmethod
    def main(miggy, aimiggy):
        # removed aimiggy.mode = 1
        running = True
        try:
            while running:
                command = miggy.check_audio()
                if command is not None:
                    aimiggy.run(command, miggy)
                time.sleep(1)
        except KeyboardInterrupt:
            miggy.stop()
            print("Miggy stopped, thanks for using MiggyOS.")

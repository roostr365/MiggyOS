import time

class AudioInterface:

    @staticmethod
    def main(miggy, aimiggy):
        if aimiggy is None:
            print("AI is not available, cannot run the audio interface.")
            return
        aimiggy.mode = 1
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


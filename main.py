print("Loading MiggyOS TM Copyright 2026 All Rights Reserved by The Miggy...")

import sys
from Miggy import Miggy
from AIMiggyController import AIMiggy
from Terminal import TerminalInterface
from Audio import AudioInterface
from MiggyGUI import MiggyGUI  # now imports our new GUI

aimiggy = AIMiggy()

def connectMiggy():
    try:
        miggy = Miggy(sys.argv[1])
        return miggy
    except Exception as e:
        print("Failed to connect to the Miggy!!! " + str(e))
        sys.exit(1)

selection = input("0 for GUI, 1 for TerminalOS and 2 for Audio: ")
if selection == "0":
    # The GUI creates its own root and runs mainloop
    MiggyGUI.launch()   # static method to launch without a pre-existing root
elif selection == "1":
    miggy = connectMiggy()
    TerminalInterface.main(miggy, aimiggy)
elif selection == "2":
    miggy = connectMiggy()
    AudioInterface.main(miggy, aimiggy)
else:
    print("Invalid selection, you sadly will not be able to use the Miggy.")

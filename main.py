print("Loading MiggyOS TM Copyright 2026 All Rights Reserved by The Miggy...")

import sys
from Miggy import Miggy
from AIMiggyController import AIMiggy
from Terminal import TerminalInterface
from Audio import AudioInterface

aimiggy = AIMiggy()

try:
    interface = sys.argv[1] if len(sys.argv) > 1 else "eth0"
    miggy = Miggy(interface)
except Exception as e:
    print("Failed to connect to the Miggy!!! " + str(e))
    sys.exit(1)
selection = input("0 for TerminalOS and 1 for Audio")
if selection == "0":
    TerminalInterface.main(miggy, aimiggy)
elif selection == "1":
    AudioInterface.main(miggy, aimiggy)
else:
    print("Invalid selection, you sadly will not be able to use the Miggy.")

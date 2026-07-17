print("Loading MiggyOS TM Copyright 2026 All Rights Reserved by The Miggy...")

import sys
from Miggy import Miggy
from AIMiggyController import AIMiggy
from Terminal import TerminalInterface
from Audio import AudioInterface

if len(sys.argv) < 2:
    print("Usage: python main.py <network interface> (e.g. python main.py eth0)")
    sys.exit(1)

try:
    aimiggy = AIMiggy()
except Exception as e:
    print("AI unavailable: " + str(e))
    aimiggy = None

try:
    miggy = Miggy(sys.argv[1])
except Exception as e:
    print("Failed to connect to the Miggy!!! " + str(e))
    sys.exit(1)
selection = input("0 for TerminalOS and 1 for Audio: ")
if selection == "0":
    TerminalInterface.main(miggy, aimiggy)
elif selection == "1":
    AudioInterface.main(miggy, aimiggy)
else:
    print("Invalid selection, you sadly will not be able to use the Miggy.")


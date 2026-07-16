print("Loading MiggyOS TM Copyright 2026 All Rights Reserved by The Miggy...")

import sys
from Miggy import Miggy
from AIMiggyController import AIMiggy
from Terminal import TerminalOS

aimiggy = AIMiggy()

try:
    miggy = Miggy(sys.argv[1])
except Exception as e:
    print("Failed to connect to the Miggy!!! " + str(e))
    sys.exit(1)
selection = input("0 for TerminalOS and 1 for Audio")
if selection == "0":
    TerminalOS.main(miggy)
elif selection == "1":
    pass
else:
    print("Invalid selection, you sadly will not be able to use the Miggy.")

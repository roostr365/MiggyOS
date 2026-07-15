print("Loading MiggyOS TM...")

import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from Miggy import Miggy as Niggy

ChannelFactoryInitialize(0, sys.argv[1])
print("Connected Succesfully!")

miggy = Niggy()


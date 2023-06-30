from enum import Enum

# Everything following the next line will be included in chat context
### START CONTEXT ###

class Distance(Enum):
    HERE = 10
    NEAR = 50
    FAR = 100

class BlockSide(Enum):
    BOTTOM = 0
    TOP = 1
    LEFT = 2
    RIGHT = 3
    FRONT = 4
    BACK = 5

class RelativeLocation(Enum):
    BOT_STANDING = 0
    BOT_LOOKING = 1
    PLAYER_STANDING = 2
    PLAYER_LOOKING = 3

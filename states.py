from enum import Enum

class BotState(Enum):
    SLEEPING = 1
    SETUP = 2
    READY = 3
    TOSSUP = 4
    WAITING = 5
    VALIDATE = 6
    BONUS = 7
    END = 8
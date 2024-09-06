# script to shuffle your playlist! generates a random number then plays that song

import random
import math
def shuffle(playlist: list):
    list = random.shuffle(playlist)
    return list
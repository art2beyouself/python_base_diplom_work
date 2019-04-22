# -*- coding: utf-8 -*-

# pip install astrobox

from astrobox.space_field import SpaceField
from zaboev import *

if __name__ == '__main__':
    scene = SpaceField(
        speed=5
    )

    for drone in range(3):
        d = RedWings()

    for drone in range(2):
        d = TruckerDron()

    scene.go()

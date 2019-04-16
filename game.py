# -*- coding: utf-8 -*-

# pip install astrobox

from astrobox.space_field import SpaceField
from zaboev import DragonDrone


if __name__ == '__main__':
    scene = SpaceField(
        speed=5,
    )
    d = DragonDrone()
    scene.go()

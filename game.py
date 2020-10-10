# -*- coding: utf-8 -*-

# pip install -r requirements.txt

from astrobox.space_field import SpaceField

from zaboev import ZaboevDrone

if __name__ == '__main__':
    scene = SpaceField(
        speed=3,
        asteroids_count=10,
    )

    for drone in range(5):
        d = ZaboevDrone()

    scene.go()

# Второй этап: зачёт!

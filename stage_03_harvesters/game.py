# -*- coding: utf-8 -*-

# pip install -r requirements.txt

from astrobox.space_field import SpaceField
from stage_03_harvesters.reaper import ReaperDrone
from stage_03_harvesters.driller import DrillerDrone
# TODO тут импортировать своих дронов
from zaboev import ZaboevDrone

NUMBER_OF_DRONES = 5

if __name__ == '__main__':
    scene = SpaceField(
        speed=5,
        asteroids_count=20,
    )
    # TODO создать их
    team_1 = [ZaboevDrone() for _ in range(NUMBER_OF_DRONES)]

    # TODO и побороть противников!
    team_2 = [ReaperDrone() for _ in range(NUMBER_OF_DRONES)]
    scene.go()


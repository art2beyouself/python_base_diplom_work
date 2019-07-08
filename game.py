# -*- coding: utf-8 -*-

# pip install -r requirements.txt
# TODO обрати внимание на изменение версии библиотеки astrobox!!!
#  надо обновить, пайчарм сам это предложит - соглашайся. Если нет - руками обновить.

from astrobox.space_field import SpaceField
from zaboev import BirdWings

if __name__ == '__main__':
    scene = SpaceField(
        speed=5,
        asteroids_count=15,
    )

    for drone in range(5):
        d = BirdWings()

    scene.go()

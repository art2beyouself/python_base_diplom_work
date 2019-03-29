# -*- coding: utf-8 -*-

# pip install astrobox

from astrobox.space_field import SpaceField
from astrobox.core import Dron


# TODO класс своего дрона назвать творчески
#  и вынести в отдельный модуль. Модуль назвать своей фамилией
class VaderDron(Dron):

    def on_born(self):
        self.move_at(self.asteroids[0])

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        self.move_at(self.my_mathership)

    def on_stop_at_mathership(self, mathership):
        self.unload_to(mathership)

    def on_unload_complete(self):
        self.move_at(self.asteroids[0])


if __name__ == '__main__':
    scene = SpaceField()
    d = VaderDron()
    scene.go()

from astrobox.core import Dron


class DragonDrone(Dron):

    def on_born(self):
        self.target = self.asteroids[0]
        self.move_at(self.get_near_target())

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        if self.free_space > 10:
            self.move_at(self.get_near_target())
        elif 0 < self.free_space <= 10 and self.distance_to(self.get_near_target()) < 10:
            self.move_at(self.get_near_target())
        else:
            self.move_at(self.my_mathership)

    def on_stop_at_mathership(self, mathership):
        self.unload_to(mathership)

    def on_unload_complete(self):
        self.move_at(self.get_near_target())

    def get_near_target(self):
        my_dict = {}
        for asteroid in self.asteroids:
            my_dict[asteroid] = self.distance_to(asteroid)
        sorted_my_dict = sorted(my_dict.items(), key=lambda kv: kv[1])

        for asteroid in sorted_my_dict:
            if asteroid[0].payload > 0:
                return asteroid[0]
        else:
            return self.my_mathership

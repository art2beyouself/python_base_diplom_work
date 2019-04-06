from astrobox.core import Dron


class DragonDrone(Dron):

    def on_born(self):
        self.move_at(self.get_near_target())

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        self.move_at(self.get_near_target())

    def on_stop_at_mathership(self, mathership):
        self.unload_to(mathership)

    def on_unload_complete(self):
        self.move_at(self.get_near_target())

    def get_near_target(self):
        targets = {}
        for asteroid in self.asteroids:
            targets[asteroid] = self.distance_to(asteroid)
        targets = dict(sorted(targets.items(), key=lambda targets: targets[1]))

        for target, distance in targets.items():
            if target.payload > 0:
                if self.free_space > 10:
                    return target
                elif 0 < self.free_space <= 10 and distance < 10:
                    return target
                else:
                    return self.my_mathership
        else:
            return self.my_mathership

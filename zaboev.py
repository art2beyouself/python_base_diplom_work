import random

from astrobox.core import Dron

busy_asteroids = []


class RedWings(Dron):
    names = ['eagle', 'kite', 'hawk', 'Jay', 'peregrine']

    def __init__(self, coord=None):
        super(RedWings, self).__init__(coord=coord)
        self.name = random.choice(RedWings.names)
        self.chosen_target = None

    def report(self):
        # TODO оформить отчет
        total_distance = 0
        for asteroid in self.asteroids:
            total_distance += self.distance_to(asteroid)
        print(self.name)
        print(f'Общая дистанция от базы до всех астеройдов (с учетом того, что лететь придётся дважды) = '
              f'{round(total_distance)*2}.')
        print('Выбранная цель=', self.chosen_target)
        print('Занятые астеройды=', busy_asteroids)
        print('---')

    def on_born(self):
        self.move_at(self.get_near_target())

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        busy_asteroids.remove(self.chosen_target)
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
                    if self.is_empty:
                        self.chosen_target =  target
                    elif self.is_full:
                        return self.my_mathership
                    elif self.payload <= 70:
                        self.chosen_target = target
                    elif self.payload > 70:
                        print(round(self.distance_to(self.my_mathership)), round(distance))
                        if self.distance_to(self.my_mathership) < distance:
                            return self.my_mathership
                        else:
                            self.chosen_target = target
                    else:
                        return self.my_mathership

                    if self.chosen_target not in busy_asteroids:
                        busy_asteroids.append(self.chosen_target)
                        return self.chosen_target
        else:
            return self.my_mathership

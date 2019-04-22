import random

from astrobox.core import Dron

busy_asteroids = []


class RedWings(Dron):
    names = ['eagle', 'kite', 'hawk', 'Jay', 'peregrine']

    def __init__(self, coord=None):
        super(RedWings, self).__init__(coord=coord)
        self.name = random.choice(RedWings.names)
        self.chosen_target = None
        self.dst_full = 0
        self.dst_part = 0
        self.dst_empty = 0

    def report(self):
        # TODO оформить отчет
        total_distance = 0
        for asteroid in self.asteroids:
            total_distance += self.distance_to(asteroid)
        print(self.name)
        print(f'Общая дистанция от базы до всех астеройдов (с учетом того, что лететь придётся дважды) = '
              f'{round(total_distance)*2}.')
        print(f'Дистанции: полным={round(self.dst_full)}, '
              f'пустым={round(self.dst_empty)}, '
              f'частично загруженным={round(self.dst_part)}.')

        print('Выбранная цель=', self.chosen_target)
        print('Занятые астеройды=', busy_asteroids)
        print('---')

    def on_born(self):
        target = self.get_near_target()
        self.calc_metric()
        self.move_at(target)

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        busy_asteroids.remove(self.chosen_target)
        target = self.get_near_target()
        self.calc_metric()
        self.move_at(target)

    def on_stop_at_mathership(self, mathership):
        self.unload_to(mathership)
        self.report()

    def on_unload_complete(self):
        target = self.get_near_target()
        self.calc_metric()
        self.move_at(target)

    def calc_metric(self):
        dst = self.distance_to(self.chosen_target)
        if self.is_full:
            self.dst_full += dst
        elif self.is_empty:
            self.dst_empty += dst
        else:
            self.dst_part += dst

    def get_near_target(self):
        targets = {}
        self.chosen_target = None
        for asteroid in self.asteroids:
            targets[asteroid] = self.distance_to(asteroid)
        targets = dict(sorted(targets.items(), key=lambda targets: targets[1]))

        for target, distance in targets.items():
            self.chosen_target = self.my_mathership
            if target.payload > 0:
                if self.is_empty:
                    self.chosen_target = target
                elif self.is_full:
                    self.chosen_target = self.my_mathership
                    break
                elif self.payload <= 70:
                    self.chosen_target = target
                elif self.payload > 70:
                    #print(round(self.distance_to(self.my_mathership)), round(distance))
                    if self.distance_to(self.my_mathership) < distance:
                        self.chosen_target = self.my_mathership
                        break
                    else:
                        self.chosen_target = target
                else:
                    self.chosen_target = self.my_mathership
                    break

                if self.chosen_target != self.my_mathership and self.chosen_target not in busy_asteroids:
                    busy_asteroids.append(self.chosen_target)
                    break
        else:
            self.chosen_target = self.my_mathership

        return self.chosen_target


class TruckerDron(RedWings):
    def get_near_target(self):
        targets = {}
        self.chosen_target = None
        for asteroid in self.asteroids:
            targets[asteroid] = self.distance_to(asteroid)
        targets = dict(sorted(targets.items(), key=lambda targets: targets[1], reverse=True))

        for target, distance in targets.items():
            self.chosen_target = self.my_mathership
            if target.payload > 0:
                if self.is_empty:
                    self.chosen_target = target
                elif self.is_full:
                    self.chosen_target = self.my_mathership
                    break
                elif self.payload <= 70:
                    self.chosen_target = target
                elif self.payload > 70:
                    if self.distance_to(self.my_mathership) < distance:
                        self.chosen_target = self.my_mathership
                        break
                    else:
                        self.chosen_target = target
                else:
                    self.chosen_target = self.my_mathership
                    break

                if self.chosen_target != self.my_mathership and self.chosen_target not in busy_asteroids:
                    busy_asteroids.append(self.chosen_target)
                    break
        else:
            self.chosen_target = self.my_mathership

        return self.chosen_target

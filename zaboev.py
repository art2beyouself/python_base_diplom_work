import random
from astrobox.core import Drone

busy_asteroids = []  # type: list


class FlyWings(Drone):
    """
        Каждому дрону рандомно выбирается класс корабля.
        Доступные классы:
            'hunter' - охотник за самыми богатыми заляжами, где больше всех ресурсов;
            'trucker' - дальнобойщик, доставляет/добывает элериум из самых дальних уголков вселенной;
            'cargo' - грузчик, доставляет/добывает элериум с ближайших астеройдов;
    """

    names = ['eagle', 'kite', 'hawk', 'Jay', 'peregrine', 'sparrow']
    ship_classes = ('hunter', 'trucker', 'cargo')

    def __init__(self, coord=None):
        super().__init__(coord=coord)
        self.name = FlyWings.names.pop()
        self.ship_class = random.choice(FlyWings.ship_classes)
        self.chosen_target = None
        self.dst_full = 0
        self.dst_part = 0
        self.dst_empty = 0

    def print_report(self):
        total = sum((self.dst_full, self.dst_empty, self.dst_part))

        print(f'{self.name} ({self.ship_class})')
        print(f'\tПройдено: \n'
              f'\t - полным = {self.dst_full} ({round((self.dst_full / total) * 100, 2)}%);')
        print(f'\t - пустым = {self.dst_empty} ({round((self.dst_empty / total) * 100, 2)}%);')
        print(f'\t - частично загруженным =  {self.dst_part} ({round((self.dst_part / total) * 100, 2)}%);')

    def on_born(self):
        self.make_decision()

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        if self.chosen_target in busy_asteroids:
            busy_asteroids.remove(self.chosen_target)
            self.make_decision()

    def on_stop_at_mothership(self, mothership):
        self.unload_to(mothership)

    def on_unload_complete(self):
        self.make_decision()
        if self.chosen_target == self.my_mothership:
            self.print_report()

    def calc_metric(self):
        dst = round(self.distance_to(self.chosen_target))
        if self.is_full:
            self.dst_full += dst
        elif self.is_empty:
            self.dst_empty += dst
        else:
            self.dst_part += dst

    def init_space_map(self):
        space_map = {}
        for asteroid in self.asteroids:
            space_map[asteroid] = {'payload': asteroid.payload,
                                   'distance': self.distance_to(asteroid)}
        return space_map

    def get_map_by_distance(self, reverse=False):
        space_map = self.init_space_map()
        prepared_targets = dict(sorted(space_map.items(), key=lambda targets: targets[1]['distance'], reverse=reverse))
        return prepared_targets

    def get_map_by_payload(self, reverse=False):
        space_map = self.init_space_map()
        prepared_targets = dict(sorted(space_map.items(), key=lambda targets: targets[1]['payload'], reverse=reverse))
        return prepared_targets

    def get_near_asteroid(self):

        for asteroid in self.get_map_by_distance():
            if asteroid.payload > 0 and asteroid not in busy_asteroids:
                return asteroid
        else:
            return self.mothership

    def chose_target(self, extraction_map):

        for target, info in extraction_map.items():
            payload, distance = info['payload'], info['distance']
            if payload > 0 and self.my_mothership.free_space > 0:

                if self.is_empty:
                    self.chosen_target = target
                elif self.is_full:
                    self.chosen_target = self.my_mothership

                elif self.payload <= self.fullness / 0.7:
                    self.chosen_target = self.get_near_asteroid()

                elif self.payload > self.fullness / 0.7:
                    if self.distance_to(self.my_mothership) < distance:
                        self.chosen_target = self.my_mothership

                    else:
                        self.chosen_target = self.get_near_asteroid()
                else:
                    self.chosen_target = self.my_mothership

                if self.chosen_target != self.my_mothership and self.chosen_target not in busy_asteroids:
                    busy_asteroids.append(self.chosen_target)
                    break
            else:
                self.chosen_target = self.my_mothership
        else:
            self.chosen_target = self.my_mothership

    def make_decision(self):
        extraction_map = {}

        if self.ship_class == 'cargo':
            extraction_map = self.get_map_by_distance(reverse=False)
        elif self.ship_class == 'trucker':
            extraction_map = self.get_map_by_distance(reverse=True)
        elif self.ship_class == 'hunter':
            extraction_map = self.get_map_by_payload(reverse=True)

        self.chose_target(extraction_map)
        self.calc_metric()
        self.move_at(self.chosen_target)

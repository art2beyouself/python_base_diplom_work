import logging
import random

from astrobox.core import Drone


class Strategy:

    busy_asteroids = []

    def __init__(self, unit=None):
        self.unit = unit

    def update_space_map(self):
        space_map = {}
        for asteroid in self.unit.asteroids:
            space_map[asteroid] = dict(payload=asteroid.payload, distance=self.unit.distance_to(asteroid))
        return space_map

    def get_map(self, order_by, reverse=False):
        space_map = self.update_space_map()
        prepared_targets = dict(sorted(space_map.items(), key=lambda targets: targets[1][order_by], reverse=reverse))
        return prepared_targets

    def mark_target_as_busy(self, target):
        if target != self.unit.mothership and target not in Strategy.busy_asteroids:
            Strategy.busy_asteroids.append(target)

    def unmark_target_as_busy(self, target):
        if target in Strategy.busy_asteroids:
            Strategy.busy_asteroids.remove(target)

    def get_near_asteroid(self):

        for asteroid in self.get_map(order_by='distance'):
            if asteroid.payload > 0 and asteroid not in Strategy.busy_asteroids:
                return asteroid
        else:
            return self.unit.mothership

    def chose_target(self, extraction_map):

        for target, info in extraction_map.items():
            payload, distance = info['payload'], info['distance']
            if payload > 0 and self.unit.mothership.free_space > 0:

                if self.unit.is_empty:
                    return target
                elif self.unit.is_full:
                    return self.unit.mothership

                elif self.unit.payload <= self.unit.fullness / 0.7:
                    return self.get_near_asteroid()

                elif self.unit.payload > self.unit.fullness / 0.7:
                    if self.unit.distance_to(self.unit.mothership) > distance:
                        return self.get_near_asteroid()
                else:
                    return self.unit.mothership
            else:
                return self.unit.mothership
        else:
            return self.unit.mothership


class CargoHunterStrategy(Strategy):

    def __init__(self, drone=None):
        super().__init__(drone)

    def get_target_map(self):
        return super().get_map(order_by='payload', reverse=True)


class CargoStrategy(Strategy):

    def __init__(self, drone=None):
        super().__init__(drone)

    def get_target_map(self):
        return super().get_map(order_by='distance', reverse=False)


class ZaboevDrone(Drone):

    names = ['eagle', 'kite', 'hawk', 'Jay', 'peregrine', 'sparrow']


    """
        Каждому дрону рандомно выбирается класс корабля.
        Доступные классы:
            'hunter' - охотник за самыми богатыми заляжами, где больше всех ресурсов;
            'trucker' - дальнобойщик, доставляет/добывает элериум из самых дальних уголков вселенной;
            'cargo' - грузчик, доставляет/добывает элериум с ближайших астеройдов;
        :param coord: Координаты создания дрона
    """

    _available_strategies = (CargoHunterStrategy, CargoStrategy)
    '''trucker'''

    fh = logging.FileHandler(filename='Game.log', delay=True)

    def __init__(self, coord=None):
        super().__init__(coord=coord)
        self.strategy = None
        self.chosen_target = None
        self.dst_full = 0
        self.dst_part = 0
        self.dst_empty = 0
        self.name = None

    def change_strategy(self, strategy):
        self.strategy = strategy(drone=self)

    def choose_random_strategy(self):
        return random.choice(ZaboevDrone._available_strategies)(drone=self)

    def on_born(self):
        self.strategy = self.choose_random_strategy()
        self.name = self.names.pop()
        self.logger.info(f'Бот {self.name} создан')
        self.make_decision()

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):
        self.strategy.unmark_target_as_busy(self.chosen_target)
        self.make_decision()

    def on_stop_at_mothership(self, mothership):
        self.unload_to(mothership)

    def on_unload_complete(self):
        self.make_decision()
        if self.chosen_target == self.my_mothership:
            self.print_metric_report()

    def calc_metric(self):
        dst = round(self.distance_to(self.chosen_target))
        if self.is_full:
            self.dst_full += dst
        elif self.is_empty:
            self.dst_empty += dst
        else:
            self.dst_part += dst

    def print_metric_report(self):
        """
            Выводит на консоль отчет о пройденном расстоянии (полным, пустым, частично загруженном)
        """
        total = sum((self.dst_full, self.dst_empty, self.dst_part))

        self.logger.info(f'{self.name} ({self.strategy})')
        self.logger.info(f'\tПройдено: \n'
                         f'\t - полным = {self.dst_full} ({round((self.dst_full / total) * 100, 2)}%);')
        self.logger.info(f'\t - пустым = {self.dst_empty} ({round((self.dst_empty / total) * 100, 2)}%);')
        self.logger.info(f'\t - частично загруженным =  {self.dst_part} ({round((self.dst_part / total) * 100, 2)}%);')

    def make_decision(self):

        extraction_map = self.strategy.get_target_map()

        self.chosen_target = self.strategy.chose_target(extraction_map)
        self.strategy.mark_target_as_busy(target=self.chosen_target)
        self.calc_metric()
        self.move_at(target=self.chosen_target)



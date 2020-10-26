from astrobox.cargo import CargoTransition
from astrobox.core import Drone, Asteroid
from robogame_engine.geometry import Point
from robogame_engine.theme import theme


class DroneState:

    def __init__(self, strategy):
        self.strategy = strategy
        self.__transition = None

    @property
    def unit(self):
        return self.strategy.unit

    @property
    def transition(self):
        return self.__transition

    @transition.setter
    def transition(self, transition):
        self.__transition = transition

    @property
    def is_finished(self):
        if self.transition and self.transition.is_finished:
            return True
        return False

    def get_next_state(self):
        pass

    def game_step(self):
        if not self.transition:
            if self.strategy.chosen_target:
                self.unit.move_at(self.strategy.chosen_target)


class DroneLoadState(DroneState):

    def __init__(self, strategy):
        super().__init__(strategy)

    def game_step(self):
        super(DroneLoadState, self).game_step()
        if self.unit.distance_to(self.strategy.chosen_target) <= theme.CARGO_TRANSITION_DISTANCE:
            self.transition = CargoTransition(cargo_from=self.strategy.chosen_target.cargo,
                                              cargo_to=self.unit.cargo)

            if self.unit.free_space < self.strategy.chosen_target.cargo.payload:
                self.unit.turn_to(self.unit.mothership)
            else:
                self.unit.turn_to(self.strategy.chosen_target)

        if self.transition:
            self.transition.game_step()


class DroneUnloadState(DroneState):

    def __init__(self, strategy):
        super(DroneUnloadState, self).__init__(strategy)

    def game_step(self):
        super(DroneUnloadState, self).game_step()

        if self.unit.distance_to(self.strategy.chosen_target) <= theme.CARGO_TRANSITION_DISTANCE:
            self.transition = CargoTransition(cargo_from=self.unit.cargo,
                                              cargo_to=self.strategy.chosen_target.cargo)

            turn_target = self.strategy.get_near_rate_asteroid()
            self.unit.turn_to(turn_target)

        if self.transition:
            self.transition.game_step()


class Strategy:

    def __init__(self, unit):
        self.__unit = unit

    @property
    def unit(self):
        return self.__unit

    def init_map_source(self):
        space_map = {}
        for asteroid in self.unit.scene.asteroids:
            distance = self.unit.distance_to(asteroid) or 1
            if asteroid.is_empty:
                continue
            space_map[asteroid] = {'rate': asteroid.payload / distance,
                                   'payload': asteroid.payload,
                                   'distance': distance}

        return space_map

    def get_asteroids_by_rate(self):
        source = self.init_map_source()
        source = dict(sorted(source.items(), key=lambda targets: targets[1]['rate'], reverse=True))
        return source

    def is_map_source_empty(self):
        return [asteroid for asteroid, asteroid_data in self.init_map_source().items() if asteroid_data['payload'] > 0]

    def game_step(self):
        pass


class HarvestStrategy(Strategy):
    busy_asteroids = []

    def __init__(self, unit):
        super().__init__(unit)
        self.chosen_target = None
        self.next_decision_distance = 0

    def get_unit_action_state(self):
        if self.unit.action_state.is_finished:
            if self.chosen_target is self.unit.mothership:
                self.unit.action_state = DroneUnloadState(strategy=self)
            else:
                self.unit.action_state = DroneLoadState(strategy=self)

    def game_step(self):

        if self.unit.action_state is None:
            self.unit.action_state = DroneLoadState(strategy=self)
            return

        # определяем цель
        self.get_harvest_target()

        # определяем действие дрона
        self.get_unit_action_state()

        self.get_harvest_target()

        # выполняем действие согласно плана
        if self.unit.action_state:
            self.unit.action_state.game_step()

    def get_harvest_target(self):
        new_target = self._chose_target()

        self.unmark_target_as_busy(self.chosen_target)
        if self.chosen_target != new_target:
            self.chosen_target = new_target
            self.mark_target_as_busy(new_target)

        self.unit.calc_metric()

    def _chose_target(self) -> Asteroid:
        for asteroid in self.get_asteroids_by_rate():

            if asteroid.is_empty:
                continue
            elif asteroid in HarvestStrategy.busy_asteroids:
                continue
            elif self.unit.is_empty:
                return asteroid
            elif self.unit.is_full:
                return self.unit.mothership
            elif not self.unit.cargo.is_full:
                return self.get_near_rate_asteroid()
            break
        return self.unit.my_mothership

    def get_near_rate_asteroid(self):
        for asteroid in self.get_asteroids_by_rate():
            return asteroid
        else:
            return self.unit.mothership

    def unmark_target_as_busy(self, target):
        if self.chosen_target in HarvestStrategy.busy_asteroids:
            HarvestStrategy.busy_asteroids.remove(target)

    def mark_target_as_busy(self, target):
        if target == self.unit.mothership or target in HarvestStrategy.busy_asteroids:
            return
        HarvestStrategy.busy_asteroids.append(target)


class BaseDrone(Drone):
    # TODO - Максимальное количество дронов - 7 (theme.MAX_DRONES_AT_TEAM). Тогда уж и задать столько имён
    NAMES = ['eagle', 'kite', 'hawk', 'peregrine', 'sparrow']

    def __init__(self, coord=None):
        # TODO - Почему в параметрах coord? Откуда это? В родительском классе просто кварги принимаются
        super().__init__(coord=coord)
        self.name = BaseDrone.NAMES.pop()
        self.dst_full = 0
        self.dst_part = 0
        self.__strategy = None
        self.dst_empty = 0

        self._last_point = Point(x=0, y=0)
        self.is_printed = False

    def __str__(self):
        return f'{self.name:^10} \t {self.fullness}'

    def print_report(self):
        if not self.is_printed:
            total = sum((self.dst_full, self.dst_empty, self.dst_part))
            if not total:
                total = 1
            print(f'{self.name} ({self.__class__.__name__})')
            print(f'\tПройдено: \n'
                  f'\t - полным = {self.dst_full} ({round((self.dst_full / total) * 100, 2)}%);')
            print(f'\t - пустым = {self.dst_empty} ({round((self.dst_empty / total) * 100, 2)}%);')
            print(f'\t - частично загруженным =  {self.dst_part} ({round((self.dst_part / total) * 100, 2)}%);')
        self.is_printed = True

    def calc_metric(self):
        current_point = Point(self.x, self.y)
        if self._last_point != current_point:
            distance_to_last_point = round(self.distance_to(self._last_point))
            if self.is_full:
                self.dst_full += distance_to_last_point
            elif self.is_empty:
                self.dst_empty += distance_to_last_point
            else:
                self.dst_part += distance_to_last_point

            self._last_point = current_point

    @property
    def strategy(self):
        return self.__strategy

    @strategy.setter
    def strategy(self, strategy):
        self.__strategy = strategy

    @strategy.deleter
    def strategy(self):
        del self.__strategy

    def game_step(self):
        super().game_step()
        self.strategy.game_step()


class ZaboevDrone(BaseDrone):
    __STRATEGY = HarvestStrategy

    def __init__(self, coord=None):
        super().__init__(coord)
        self.__state = None

    def on_born(self):
        self.strategy = self.__STRATEGY(unit=self)

    @property
    def action_state(self):
        return self.__state

    @action_state.setter
    def action_state(self, state):
        self.__state = state

    def __repr__(self):
        return f'{self.name} payload={self.cargo.payload} state={self.action_state}'

    def __str__(self):
        base_str = super(ZaboevDrone, self).__str__()
        return base_str + f'\t state={type(self.action_state).__name__}'

    def game_step(self):
        super().game_step()
        self.strategy.game_step()

        if not self.strategy.is_map_source_empty():
            self.strategy.unit.print_report()

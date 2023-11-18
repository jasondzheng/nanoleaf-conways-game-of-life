from dataclasses import dataclass

import argparse
import random
import threading
import time
import yaml

from nanoleaf import NanoleafCanvasGridCluster, PanelUpdate
from conwaysgameoflife import ConwaysGameOfLife

@dataclass
class ConwaysGameOfLifeNanoleaf():
    ip: str
    key: str
    random_spawn_rate_lives: int = 4
    random_spawn_rate_ticks: int = 6
    tick_seconds: float = 0.8
    alive_color_r: int = 0
    alive_color_g: int = 255
    alive_color_b: int = 255
    dead_color_r: int = 255
    dead_color_g: int = 255
    dead_color_b: int = 255
    
    def __post_init__(self):
        self._cluster = NanoleafCanvasGridCluster(self.ip, self.key)
        self._game_state = ConwaysGameOfLife(self._cluster.x_size, self._cluster.y_size)

        self._cluster.init_streaming()

    def loop(self):
        i = 0
        while True:
            self._game_state.tick()
            # TODO: Make spawing more organic; maybe:
            # - spawn at irregular intervals
            # - spawn with differnt colors
            if i % self.random_spawn_rate_ticks == 0:
                for _ in range(self.random_spawn_rate_lives):
                    self._game_state.set(random.randint(0, self._cluster.x_size - 1), random.randint(0, self._cluster.y_size - 1))

            updates = [
                PanelUpdate(
                    panel_id=self._cluster.lookup_panel_id(x, y),
                    r=self.alive_color_r if alive else self.dead_color_r,
                    g=self.alive_color_g if alive else self.dead_color_g,
                    b=self.alive_color_b if alive else self.dead_color_b,
                    t=int(self.tick_seconds * 10 // 2)
                ) for x, y, alive in self._game_state.dump_state() if self._cluster.lookup_panel_id(x, y) is not None
            ]  
            print(updates)
            self._cluster.stream_updates(updates)

            i = (i + 1) % self.random_spawn_rate_ticks
            time.sleep(self.tick_seconds)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog='Nanoleaf Controller',
                description='Simple python script for streaming updates to local Nanoleafs')
    parser.add_argument('config')

    with open(parser.parse_args().config, 'r') as stream:
        config = yaml.safe_load(stream)
        for k, v in config.items():
            cluster = ConwaysGameOfLifeNanoleaf(**v)
            threading.Thread(target=cluster.loop).start()
        

    

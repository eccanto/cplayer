from pathlib import Path

from cplayer.src.elements.config import Config


__DEFAULT_CONFIG = Path(__file__).parent.parent.parent.joinpath('resources/config/default.yaml')

CONFIG = Config(default_data=__DEFAULT_CONFIG)

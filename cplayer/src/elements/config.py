"""Module that defines the Config class, which is used to load, manipulate, and save configuration files.

The Config class is built on top of the third-party `dotmap` package, which provides a convenient way to access and
manipulate nested dictionaries as if they were objects with dot notation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import yaml
from dotmap import DotMap

from cplayer.src.utils.singleton import Singleton


@dataclass
class PlaylistType:
    """Playlist option fields."""

    directory: str
    selected: Optional[str]
    order: str


@dataclass
class GeneralType:
    """General option fields."""

    playlist: PlaylistType


@dataclass
class StyleType:
    """Style option fields."""

    footer: bool


@dataclass
class AppearanceType:
    """Appearance option fields."""

    style: StyleType


@dataclass
class DevelopmentType:
    """Development option fields."""

    logfile: str
    level: str


@dataclass
class DataType:
    """Data option fields."""

    general: GeneralType
    appearance: AppearanceType
    development: DevelopmentType

    toDict: Callable[[], Dict[str, Any]]  # noqa: N815


class Config(Singleton):  # pylint: disable=too-few-public-methods
    """A class for reading and writing YAML configuration files and accessing the data as attributes.

    :Example:

    >>> config = Config('config.yaml')
    >>> print(config.data.general.playlist.directory)
    ~/test_directory
    >>> config.data.general.playlist.order = 'ascending'
    >>> config.save()
    """

    DEFAULT_PATH = Path('~/.pyplayer/config.yaml').expanduser()

    data: DataType

    def __init__(self, path: Path = DEFAULT_PATH, default_data: Optional[Path] = None) -> None:
        """Initialize the Config object.

        :param path: Path to the YAML file.

        :raises FileNotFoundError: If the YAML file does not exist.
        """
        self._path = path

        if self._path.exists():
            with open(path, encoding='UTF-8') as yaml_file:
                self.data = DotMap(yaml.safe_load(yaml_file), _dynamic=False)
        elif default_data is not None and default_data.exists():
            with open(default_data, encoding='UTF-8') as yaml_file:
                self.data = DotMap(yaml.safe_load(yaml_file), _dynamic=False)

            self.save()

        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def save(self):
        """Save the configuration data to the YAML file."""
        with open(self._path, 'w', encoding='UTF-8') as yaml_file:
            yaml.dump(self.data.toDict(), yaml_file, sort_keys=False)

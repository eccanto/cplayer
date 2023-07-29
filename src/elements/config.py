"""Module that defines the Config class, which is used to load, manipulate, and save configuration files.

The Config class is built on top of the third-party `dotmap` package, which provides a convenient way to access and
manipulate nested dictionaries as if they were objects with dot notation.
"""
from pathlib import Path
from typing import Any, Optional

import yaml
from dotmap import DotMap

from src.utils.singleton import Singleton


class Config(Singleton):
    """A class for reading and writing YAML configuration files and accessing the data as attributes.

    :Example:

    >>> config = Config('config.yaml')
    >>> print(config.database.host)
    localhost
    >>> config.database.port = 5432
    >>> config.save()
    """

    DEFAULT_PATH = Path('~/.pyplayer/config.yaml').expanduser()

    def __init__(self, path: Path = DEFAULT_PATH, default_data: Optional[Path] = None) -> None:
        """Initialize the Config object.

        :param path: Path to the YAML file.

        :raises FileNotFoundError: If the YAML file does not exist.
        """
        self._path = path

        if self._path.exists():
            with open(path, encoding='UTF-8') as yaml_file:
                self._data = DotMap(yaml.safe_load(yaml_file), _dynamic=False)
        elif default_data is not None and default_data.exists():
            with open(default_data, encoding='UTF-8') as yaml_file:
                self._data = DotMap(yaml.safe_load(yaml_file), _dynamic=False)

            self.save()

        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def __getattr__(self, attribute: str) -> Any:
        """Gets the attribute value.

        :param attribute: Attribute name.

        :return: The attribute value.
        """
        return super().__getattribute__('_data')[attribute]

    def __setattr__(self, name: str, value: Any) -> None:
        """Sets the attribute value.

        :param name: Attribute name.
        :param value: Attribute value.
        """
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            setattr(super().__getattribute__('_data'), name, value)

    def save(self):
        """Save the configuration data to the YAML file."""
        with open(self._path, 'w', encoding='UTF-8') as yaml_file:
            yaml.dump(self._data.toDict(), yaml_file, sort_keys=False)

"""Singleton pattern implementation."""

from typing import Any, Dict, Type


class Singleton:  # pylint: disable=too-few-public-methods
    """Singleton Class that represents the implementation of the Singleton design pattern."""

    _instances: Dict[Type['Singleton'], Any] = {}

    def __new__(cls, *_args, **_kwargs):
        """Creates a new instance of the Singleton class or return an existing instance if available.

        :param *_args: Variable length argument list.
        :param **_kwargs: Arbitrary keyword arguments.

        :returns: An instance of the Singleton class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls)
        return cls._instances[cls]

"""Module to define the Playlist class that represents a collection of songs and their metadata."""

import json
from pathlib import Path
from typing import Optional


class PlayList:
    """Playlist class."""

    def __init__(self, path: Path) -> None:
        """Initializes the Widget object.

        :param path: The path to the playlist file.
        """
        self.path = path
        self.name = self.path.stem.title()

        if self.path.exists():
            data = json.loads(self.path.read_text(encoding='UTF-8'))

            self.selected: Optional[Path] = data['selected']
            self.songs = [Path(song_path) for song_path in data['songs']]
        else:
            self.selected = None
            self.songs = []

    def save(self) -> None:
        """Saves the playlist data to the file."""
        with open(self.path, 'w', encoding='UTF-8') as json_file:
            json.dump(
                {
                    'name': self.name,
                    'path': str(self.path),
                    'selected': str(self.selected) if self.selected else None,
                    'songs': [str(path) for path in self.songs],
                },
                json_file,
                indent=2,
            )

    def select(self, path: Path) -> None:
        """Sets the selected song in the playlist and save the playlist data.

        :param path: The path to the selected song.
        """
        self.selected = path
        self.save()

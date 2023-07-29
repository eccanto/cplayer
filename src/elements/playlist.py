import json
from pathlib import Path
from typing import Optional


class PlayList:
    def __init__(self, path: Path) -> None:
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
        self.selected = path
        self.save()

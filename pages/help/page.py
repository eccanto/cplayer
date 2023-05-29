from pathlib import Path
from textwrap import dedent

from textual.app import ComposeResult
from textual.widgets import MarkdownViewer
from components.hidden_widget.widget import HiddenWidget


class HelpPage(HiddenWidget):
    DEFAULT_CSS = Path(__file__).parent.joinpath('styles.css').read_text()

    _CONTENT = dedent(
        '''
        # Simple Song Player

        Basic song player writren with Python ([textual](https://textual.textualize.io/)).

        ## Features

        - Reproduce songs from a directory.
        - Create multiple playlists and manage then.
        - Customized GUI.

        ## Keymaps

        Available keymaps.

        | Keymap          | window     | Description                        |
        | --------------- | ---------- | ---------------------------------- |
        | q               | `all`      | Quit application                   |
        | i               | `all`      | go to Information Page             |
        | h               | `all`      | go to Home Page                    |
        | space           | `playlist` | Play/Pause                         |
        | -               | `playlist` | Decrease Volume                    |
        | +               | `playlist` | Increase Volume                    |
        | l               | `playlist` | Load Playlist                      |
        | d               | `playlist` | Load Directory                     |
        | p               | `playlist` | Previous                           |
        | n               | `playlist` | Next                               |
        | r               | `playlist` | Restart                            |
        | s               | `playlist` | Search                             |
        | f               | `playlist` | Filter                             |
        | S               | `playlist` | Save Playlist                      |
        | delete          | `playlist` | Delete Song                        |
        | A               | `playlist` | Add songs                          |
        | ctrl+up         | `playlist` | Up Song                            |
        | ctrl+down       | `playlist` | Down Song                          |

        ## Configuration

        The GUI can be configured using the configuration file `~/.config/simple-player/config.json`

        ```json
        {
            "icons": {
                "playlist": "",
                "song": "♪",
                "volume": "",
                "reproduce": "❱",
                "filter": "",
                "directory": "",
                "add_songs": ""
            }
        }
        ```

        ## TODO

        - Add confirmation dialog to remove/add songs.
        - Add file explorer to add songs from a directory.
        - Extend the configuration file to enable more customizations.
        '''
    ).strip()

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(self._CONTENT, show_table_of_contents=True)

    def focus(self) -> None:
        viewer = self.query_one(MarkdownViewer)
        viewer.focus()

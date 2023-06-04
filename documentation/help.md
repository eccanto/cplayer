# Simple Song Player

Basic song player written with Python ([github](https://github.com/eccanto/simple-song-player)).

## Features

- Customized GUI.
- Create multiple playlists and manage then.
- Custom playlist sort.

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
- Add "recent" sections: recent folders, recent playlist, rencet songs.

from pathlib import Path
import time
import click
import numpy
from pygame import mixer
from mutagen.mp3 import MP3
# import keyboard as kb
from pynput import keyboard
import os
from rich.layout import Layout
from rich.align import Align
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich import box
from pydub import AudioSegment

player = mixer

default_theme = {
    'panel_border': '#0066CC',
    'spectrum_color': '#17E200',
}

__TITLE_COLOR = '#C0C0C0'


song_idx = 0
currently_playing = None
music_list = []


def exit_player():
    player.music.stop()
    os._exit(0)


def play_n_pause():
    if player.music.get_busy():
        player.music.pause()
    else:
        player.music.unpause()


def next_track():
    global song_idx, currently_playing

    song_idx = music_list.index(currently_playing)
    if song_idx == len(music_list):
        song_idx = 0
    elif song_idx < len(music_list):
        song_idx = song_idx + 1
    if len(music_list) > 0:
        currently_playing = music_list[song_idx]
    # currently_playing = music_list[song_idx]
    player.music.load(currently_playing)
    player.music.play()


def prev_track():
    global song_idx, currently_playing

    song_idx = music_list.index(currently_playing)
    if song_idx == 0:
        song_idx = len(music_list)
    elif song_idx > 0:
        song_idx = song_idx - 1
    if len(music_list) > 0:
        currently_playing = music_list[song_idx]
    player.music.load(currently_playing)
    player.music.play()


def increase_vol():
    curr_vol = player.music.get_volume()
    if curr_vol > 1:
        curr_vol = 1
    else:
        curr_vol = curr_vol + 0.1
    player.music.set_volume(curr_vol)


def decrease_vol():
    curr_vol = player.music.get_volume()
    if curr_vol < 0:
        curr_vol = 0
    else:
        curr_vol = curr_vol - 0.1
    player.music.set_volume(curr_vol)


def user_controls():
    listener = keyboard.GlobalHotKeys({
        'p': play_n_pause,
        'r': lambda: player.music.rewind(),
        's': lambda: player.music.stop(),
        'v': prev_track,
        'n': next_track,
        '+': increase_vol,
        '-': decrease_vol,
        'q': exit_player,
    })
    listener.start()
    listener.wait()


def draw_ui(layout):
    layout.split(
        Layout(name='main'),
    )

    layout['main'].split_row(
        Layout(name='player'),
    )

    layout['player'].split_column(
        Layout(name='media_n_spectrum'),
        Layout(name='now_playing', size=3),
    )

    layout['media_n_spectrum'].split_row(
        Layout(name='song_list'),
        Layout(name='spectrum', size=11),
    )

    return layout


def generate_playlist(layout, song_list):
    global currently_playing

    currently_playing_name = os.path.basename(currently_playing.split('\\')[-1].replace('.mp3', ''))
    table = Table(
        show_lines=False,
        box=box.SIMPLE,
        border_style=default_theme['panel_border'],
        expand=True,
    )
    table.add_column('Name', justify='left', style='cyan', no_wrap=False)
    table.add_column('Duration', justify='right', style='green')

    for index, song in enumerate(song_list):
        song_meta = MP3(song)
        dur = time_format(song_meta.info.length)
        name = os.path.basename(song.split('\\')[-1].replace('.mp3', ''))

        table.add_row(f'[#3fff2d]{"▸" if (currently_playing_name == name) else " "} [#00CCCC]♪ ╼ [#FFB266]{name}', dur)

    return Panel(
        table,
        border_style=default_theme['panel_border'],
        title=f'[bold][{__TITLE_COLOR}] ♪  Pochita playlist [/{__TITLE_COLOR}][/bold]',
        box=box.SQUARE,
        expand=True,
    )


def time_format(seconds):
    return '[#FFB266]%02d:%02d' % (seconds // 60, seconds % 60)


def spectrumgram(sz):
    if not len(sz):
        return ''

    max_value = max(sz)
    grades = [v/max_value for v in sz] if max_value else []
    return ' '.join([f'[rgb({int(255 * v)},{int(255 * v)},{int(255 * v)})]●' for v in grades])


@click.command()
@click.option( '-s', '--songs', help=f'Songs directory.', type=click.Path(exists=True, path_type=Path), required=True)
def main(songs):
    global song_idx, currently_playing, music_list

    layout = Layout(name='root')
    layout = draw_ui(layout)

    # Starting the mixer
    player.init()

    # Loading the song
    for file in os.listdir(songs):
        if file.endswith('.mp3'):
            music_list.append(os.path.join(songs, file))

    currently_playing = music_list[0]

    song_idx = 0
    currently_playing_name = currently_playing.split('\\')[-1].replace('.mp3', '')

    song = AudioSegment.from_mp3(currently_playing)
    sampleRate = song.frame_rate

    audioBuffer = numpy.array(song.get_array_of_samples())

    player.music.load(currently_playing)
    for m in music_list:
        if not m == currently_playing:
            player.music.queue(m)

    song_meta = MP3(currently_playing)
    song_length = song_meta.info.length

    # Setting the volume
    player.music.set_volume(0.5)

    # Start playing the song
    player.music.play()

    user_controls()

    with Live(layout, refresh_per_second=4, screen=True):
        while True:
            layout['song_list'].update(generate_playlist(layout, music_list))

            amp = []
            curr_ms = int(player.music.get_pos() * sampleRate / 1000)
            amp.append(audioBuffer[curr_ms])
            amp = audioBuffer[curr_ms : curr_ms + 100 : 3]
            layout['spectrum'].update(
                Panel(
                    Align.center(spectrumgram(amp), vertical='middle'),
                    border_style=default_theme['panel_border'],
                    style=default_theme['spectrum_color'],
                    box=box.SQUARE,
                )
            )

            curr_pos = int(player.music.get_pos() / 1000)
            seek_percent = int(curr_pos * 100 / song_length)

            seek_bar_str = '[#3fff2d]━' * int(seek_percent) + '[white]█' + '[#004C99]━' * (100 - int(seek_percent))
            curr_vol = player.music.get_volume()
            vol_percent = int(curr_vol * 10)
            vol_bar_str = '[#9933FF]━' * int(vol_percent) + '[#9933FF]█' + '[#004C99]━' * (10 - int(vol_percent))

            currently_playing_name = os.path.basename(currently_playing.split('\\')[-1].replace('.mp3', ''))
            layout['now_playing'].update(
                Panel(
                    Align.center(
                        f'{time_format(curr_pos)} {seek_bar_str} {time_format(song_length)}    [white][{vol_bar_str}][/white]'
                    ),
                    title=f'Song: [{__TITLE_COLOR}]{currently_playing_name}',
                    border_style=default_theme['panel_border'],
                    box=box.SQUARE,
                )
            )

            time.sleep(0.25)


if __name__ == '__main__':
    main()

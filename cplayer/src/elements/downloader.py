"""Audio Downloader.

This module defines `Downloaders` classes that allows you to download audio from a video URL.
"""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from yt_dlp import YoutubeDL


class YoutubeDownloader:  # pylint: disable=too-few-public-methods
    """YouTube Downloader Class."""

    def __init__(self, url: str) -> None:
        """Constructor method.

        :param url: The YouTube video URL to download audio from.
        """
        self.url = url

    def download(self) -> None:
        """Starts the download process.

        This method initiates the download of the audio from the provided YouTube video URL. It saves the downloaded
        audio file as an MP3 with a title-based filename in the current directory.
        """
        with TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            options = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_directory.joinpath('%(title)s.mp3')),
                'quiet': False,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                ],
            }
            with YoutubeDL(options) as downloader:
                information = downloader.extract_info(self.url, download=False)
                if information:
                    downloader.download([self.url])

                    name = Prompt.ask('song Name', default=information['fulltitle'])
                    path = Prompt.ask('destination Path', default=str(Path('.').absolute()))
                    destination = Path(path).joinpath(f'{name}.mp3')

                    downloaded_file = next(output_directory.glob('*.mp3'))
                    shutil.copy(downloaded_file, destination)

                    console = Console()
                    text = Text.assemble('\ndownloaded file: ', (str(destination), 'bold magenta'))
                    console.print(text)

import subprocess

from assertpy import assert_that

from cplayer import __version__


def test_version_option():
    result = subprocess.run(['cplayer', '--version'], capture_output=True, text=True)

    assert_that(result.returncode).described_as(result.stderr).is_equal_to(0)
    assert_that(result.stdout).contains(__version__)

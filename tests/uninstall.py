"""Pytest test cases for uninstall the package."""

import json
import subprocess
from typing import List

from assertpy import assert_that


class TestUninstall:
    """Test cases for uninstalling the package using pip."""

    def _installed_packages(self) -> List[str]:
        """Retrieve a list of installed packages using `pip list --format json`.

        :returns: List of installed package names.
        """
        command_output = subprocess.run(['pip', 'list', '--format', 'json'], stdout=subprocess.PIPE)
        return [package_data['name'] for package_data in json.loads(command_output.stdout.decode())]

    def test_uninstall(self) -> None:
        """Test the uninstallation of the package.

        :raises AssertionError: If the package is still present after uninstallation.
        """
        assert_that(self._installed_packages()).contains('cplayer')

        subprocess.run(['pip', 'uninstall', '-y', 'cplayer'])
        assert_that(self._installed_packages()).does_not_contain('cplayer')

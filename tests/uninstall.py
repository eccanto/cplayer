"""Pytest test cases for uninstall the package."""

import pip
import pkg_resources
from assertpy import assert_that


class TestUninstall:
    """Test cases for uninstalling the package using pip."""

    @staticmethod
    def _installed_packages() -> list[str]:
        """Retrieve a list of installed packages using `pip list --format json`.

        :returns: List of installed package names.
        """
        return [package.key for package in pkg_resources.working_set]

    def test_uninstall(self) -> None:
        """Test the uninstallation of the package.

        :raises AssertionError: If the package is still present after uninstallation.
        """
        assert_that(self._installed_packages()).contains('cplayer')

        pip.main(['main', 'cplayer'])
        assert_that(self._installed_packages()).does_not_contain('cplayer')

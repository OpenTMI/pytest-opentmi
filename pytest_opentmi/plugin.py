"""
pytest plugin
"""
import os
# app modules
from . import __version__
from .OpenTmiReport import OpenTmiReport


# pytest: disable=unused-argument
def pytest_report_header(config):
    """
    header hook
    :param config: unused
    :return: None
    """
    return f'pytest-opentmi version: {__version__}'


def pytest_addoption(parser):
    """
    add option hook
    :param parser: argparser
    :return: None
    """
    group = parser.getgroup("opentmi reporting")
    group.addoption(
        "--opentmi",
        action="store",
        metavar="host",
        default=None,
        help="Opentmi host",
    )
    group.addoption(
        "--opentmi_token",
        action="store",
        metavar="token",
        default=os.environ.get('OPENTMI_TOKEN', None),
        help="Opentmi access token",
    )


def pytest_configure(config):
    """
    configure hook
    :param config: unused
    :return: None
    """
    host = config.getoption("opentmi")
    if host:
        if not hasattr(config, "slaveinput"):
            # prevent opening opentmi reporter on slave nodes (xdist)
            config._opentmi = OpenTmiReport(config)
            config.pluginmanager.register(config._opentmi)


def pytest_unconfigure(config):
    """
    unconfigure hook
    :param config: unused
    :return: None
    """
    opentmi = getattr(config, "_opentmi", None)
    if opentmi:
        del config._opentmi
        config.pluginmanager.unregister(opentmi)

import os
# app modules
from . import __version__
from .OpenTmiReport import OpenTmiReport


def pytest_report_header(config):
    return f'pytest-opentmi version: {__version__}'


def pytest_addoption(parser):
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
    host = config.getoption("opentmi")
    if host:
       if not hasattr(config, "slaveinput"):
            # prevent opening opentmi reporter on slave nodes (xdist)
            config._opentmi = OpenTmiReport(host, config)
            config.pluginmanager.register(config._opentmi)


def pytest_unconfigure(config):
    opentmi = getattr(config, "_opentmi", None)
    if opentmi:
        del config._opentmi
        config.pluginmanager.unregister(opentmi)

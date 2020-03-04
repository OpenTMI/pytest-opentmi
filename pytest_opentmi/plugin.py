from . import __version__, __pypi_url__
from opentmi import opentmi


def pytest_addhooks(pluginmanager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting")
    group.addoption(
        "--opentmi",
        action="store",
        dest="opentmi",
        metavar="host",
        default=None,
        help="Opentmi host",
    )


def pytest_configure(config):
    host = config.getoption("opentmi")
    if host:
       if not hasattr(config, "slaveinput"):
            # prevent opening htmlpath on slave nodes (xdist)
            config._opentmi = OpenTmiReport(host, config)
            config.pluginmanager.register(config._opentmi)


def pytest_unconfigure(config):
    opentmi = getattr(config, "_opentmi", None)
    if opentmi:
        del config._opentmi
        config.pluginmanager.unregister(opentmi)


class OpenTmiReport:
    def __init__(self, host, config):
        self.logfile = os.path.abspath(logfile)
        self.test_logs = []
        self.results = []
        self.errors = self.failed = 0
        self.passed = self.skipped = 0
        self.xfailed = self.xpassed = 0
        has_rerun = config.pluginmanager.hasplugin("rerunfailures")
        self.rerun = 0 if has_rerun else None
        self.self_contained = config.getoption("self_contained_html")
        self.config = config

import os
import time
import datetime
import multiprocessing
import uuid
# 3rd party modules
from joblib import Parallel, delayed
from opentmi_client.utils.exceptions import TransportException
from opentmi_client import OpenTmiClient, Result
from urllib3.exceptions import NewConnectionError
# app modules
from . import __version__, __pypi_url__
from . import hooks


def pytest_addhooks(pluginmanager):
    pluginmanager.add_hookspecs(hooks)


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


class OpenTmiReport:
    def __init__(self, host, config):
        self.test_logs = []
        self.results = []
        self.errors = self.failed = 0
        self.passed = self.skipped = 0
        self.xfailed = self.xpassed = 0
        self.suite_start_time = None
        self._sessionid = str(uuid.uuid1())
        has_rerun = config.pluginmanager.hasplugin("rerunfailures")
        self.rerun = 0 if has_rerun else None
        self.config = config
        self._client = OpenTmiClient(host)

    def append_passed(self, report):
        if report.when == "call":
            result = Result(tcid=report.head_line)
            result.execution.verdict = 'pass'
            result.execution.duration = report.duration
            if hasattr(report, "wasxfail"):
                self.xpassed += 1
                result.execution.note = 'xpass'

            else:
                self.passed += 1
            self.results.append(result)

    def append_failed(self, report):
        result = Result(tcid=report.head_line)
        result.execution.duration = report.duration
        if getattr(report, "when", None) == "call":
            result.execution.verdict = 'fail'
            if hasattr(report, "wasxfail"):
                # pytest < 3.0 marked xpasses as failures
                self.xpassed += 1
                result.execution.note = 'xfail'
            else:
                self.failed += 1
        else:
            self.errors += 1
            result = Result(tcid=report.head_line)
            result.execution.verdict = 'error'
        self.results.append(result)

    def append_skipped(self, report):
        result = Result(tcid=report.head_line)
        result.execution.duration = report.duration
        result.execution.verdict = 'skip'
        if hasattr(report, "wasxfail"):
            self.xfailed += 1
            result.execution.note = 'xskil'
        else:
            self.skipped += 1
        self.results.append(result)

    def append_other(self, report):
        # For now, the only "other" the plugin give support is rerun
        self.rerun += 1
        result = Result(tcid=report.head_line)
        result.execution.duration = report.duration
        result.execution.verdict = 'inconclusive'
        result.execution.note = 'rerun'
        result.job.id

    def _upload_report(self, session, result: Result):
        result.campaign = session.name
        result.campaign.id = self._sessionid
        result.execution.environment.framework = 'pytest'
        result.
        result.execution.profiling = dict(
            suite=dict(
                duration=self._suite_time_delta
            ),
            numtests=self._numtests,
            generated_at=self._generated
        )

        try:
            print(result)
            #self._client.post_result(result)
        except (TransportException, ConnectionRefusedError, NewConnectionError):
            pass

    def _upload_reports(self, session):
        suite_stop_time = time.time()
        self._suite_time_delta = suite_stop_time - self.suite_start_time
        self._numtests = self.passed + self.failed + self.xpassed + self.xfailed
        self._generated = datetime.datetime.now()

        num_cores = multiprocessing.cpu_count()
        Parallel(n_jobs=num_cores, backend='threading')(delayed(self._upload_report)(session, result) for result in self.results)

    def pytest_runtest_logreport(self, report):
        if report.passed:
            self.append_passed(report)
        elif report.failed:
            self.append_failed(report)
        elif report.skipped:
            self.append_skipped(report)
        else:
            self.append_other(report)

    def pytest_collectreport(self, report):
        if report.failed:
            self.append_failed(report)

    def pytest_sessionstart(self, session):
        self.suite_start_time = time.time()

    def pytest_sessionfinish(self, session):
        self._upload_reports(session)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep("-", f"Results uploaded to OpenTMI")

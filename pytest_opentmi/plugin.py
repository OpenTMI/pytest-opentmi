import os
import time
import datetime
import multiprocessing
import uuid
import pkg_resources
# 3rd party modules
from joblib import Parallel, delayed
from opentmi_client.utils.exceptions import TransportException
from opentmi_client import OpenTmiClient, Result
from opentmi_client.api import Dut, File
from urllib3.exceptions import NewConnectionError
# app modules
from . import __version__


def get_pytest_info():
    return pkg_resources.get_distribution("pytest")


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


class OpenTmiReport:
    def __init__(self, host, config):
        self.test_logs = []
        self.results = []
        self.errors = self.failed = 0
        self.passed = self.skipped = 0
        self.xfailed = self.xpassed = 0
        self.suite_start_time = None
        has_rerun = config.pluginmanager.hasplugin("rerunfailures")
        self.rerun = 0 if has_rerun else None
        self.config = config
        self._client = OpenTmiClient(host)

    def _append_passed(self, report):
        if report.when == "call":
            result = OpenTmiReport._new_result(report)
            result.execution.verdict = 'pass'
            if hasattr(report, "wasxfail"):
                self.xpassed += 1
                result.execution.note = 'xpass'
            else:
                self.passed += 1
            self.results.append(result)

    def _append_failed(self, report):
        result = OpenTmiReport._new_result(report)
        result.execution.note = f'{report.longrepr.reprcrash.message}\n' \
                                f'{report.longrepr.reprcrash.path}:{report.longrepr.reprcrash.lineno}'
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
            result.execution.verdict = 'error'
        self.results.append(result)

    def _append_skipped(self, report):
        result = OpenTmiReport._new_result(report)
        result.execution.verdict = 'skip'
        result.execution.note = report.longrepr[2]
        if hasattr(report, "wasxfail"):
            self.xfailed += 1
            result.execution.note = 'xskil'
        else:
            self.skipped += 1
        self.results.append(result)

    def _append_inconclusive(self, report):
        # For now, the only "other" the plugin give support is rerun
        result = OpenTmiReport._new_result(report)
        result.execution.verdict = 'inconclusive'
        result.execution.note = f'{report.longrepr.reprcrash.message}\n' \
                                f'{report.longrepr.reprcrash.path}:{report.longrepr.reprcrash.lineno}'
        self.results.append(result)

    def _append_other(self, report):
        # For now, the only "other" the plugin give support is rerun
        self.rerun += 1
        result = OpenTmiReport._new_result(report)
        result.execution.verdict = 'inconclusive'
        result.execution.note = 'rerun'
        self.results.append(result)

    def append_other(self, report):
        # For now, the only "other" the plugin give support is rerun
        self.rerun += 1
        result = OpenTmiReport._new_result(report)
        result.execution.verdict = 'inconclusive'
        result.execution.note = 'rerun'
        self.results.append(result)

    @staticmethod
    def _new_result(report):
        result = Result(tcid=report.nodeid)
        pytest_info = get_pytest_info()
        result.execution.duration = report.duration
        result.execution.environment.framework.name = pytest_info.project_name
        result.execution.environment.framework.version = pytest_info.version
        result.job.id = os.environ.get('JOB_NAME', str(uuid.uuid1()))
        result.execution.profiling = dict()
        if report.user_properties:
            result.execution.profiling['properties'] = dict()
        for (key, value) in report.user_properties:
            result.execution.profiling['properties'][key] = value
        if report.keywords:
            result.execution.profiling['keywords'] = []
        for key in report.keywords:
            result.execution.profiling['keywords'].append(key)

        if report.capstdout:
            log_file = File()
            log_file.set_file_data(report.capstdout)
            log_file.name = "stdout"
            log_file.mime_type = "txt"
            result.execution.append_log(log_file)

        if report.capstderr:
            log_file = File()
            log_file.set_file_data(report.capstderr)
            log_file.name = "stderr"
            log_file.mime_type = "txt"
            result.execution.append_log(log_file)

        return result

    def _link_session(self, session, result):
        result.campaign = session.name
        # dut = Dut()
        # dut.serial_number = ''
        # result.append_dut(dut)

        result.execution.profiling['suite'] = dict(duration=self._suite_time_delta)
        result.execution.profiling['numtests'] = self._numtests
        result.execution.profiling['generated_at'] = self._generated.isoformat()

    def _upload_report(self, result: Result):
        try:
            pass
            self._client.post_result(result)
        except (TransportException, ConnectionRefusedError, NewConnectionError):
            pass

    def _upload_reports(self, session):
        suite_stop_time = time.time()
        self._suite_time_delta = suite_stop_time - self.suite_start_time
        self._numtests = self.passed + self.failed + self.xpassed + self.xfailed
        self._generated = datetime.datetime.now()

        [self._link_session(session, result) for result in self.results]

        [print(result.data) for result in self.results]

        num_cores = multiprocessing.cpu_count()
        Parallel(n_jobs=num_cores, backend='threading')(delayed(self._upload_report)(result) for result in self.results)

    # pytest hooks

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            # after test
            if report.passed:
                self._append_passed(report)
            elif report.failed:
                self._append_failed(report)
            elif report.skipped:
                self._append_skipped(report)
            else:
                self._append_other(report)
        elif report.when == 'setup':
            if report.failed:
                self._append_inconclusive(report)
            elif report.skipped:
                self._append_skipped(report)

    def pytest_collectreport(self, report):
        if report.failed:
            self._append_failed(report)

    def pytest_sessionstart(self, session):
        self.suite_start_time = time.time()

    def pytest_sessionfinish(self, session):
        self._upload_reports(session)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep("-", f"Results uploaded to OpenTMI")

"""
OpenTmiReport module
"""
import os
import time
import datetime
import multiprocessing
import uuid
# 3rd party modules
from joblib import Parallel, delayed
from opentmi_client import OpenTmiClient, Result
from opentmi_client.api import Dut, File, Provider
# app modules
from . import __pytest_info__


# pylint: disable=too-many-instance-attributes
class OpenTmiReport:
    """
    OpenTmiReport class
    """
    def __init__(self, config):
        """
        Constructor
        :param config: pytest config object
        """
        self.test_logs = []
        self.results = []
        self.errors = self.failed = 0
        self.passed = self.skipped = 0
        self.xfailed = self.xpassed = 0
        self._uploaded_failed = 0
        self._uploaded_success = 0
        self._suite_time_delta = None
        self._numtests = None
        self._generated = None
        self.suite_start_time = None
        has_rerun = config.pluginmanager.hasplugin("rerunfailures")
        self.rerun = 0 if has_rerun else None
        self.config = config
        host = config.getoption("opentmi")
        self._client = OpenTmiClient(host)

    def _append_passed(self, report):
        if report.when == "call":
            result = self._new_result(report)
            result.execution.verdict = 'pass'
            if hasattr(report, "wasxfail"):
                self.xpassed += 1
                result.execution.note = 'xpass'
            else:
                self.passed += 1
            self.results.append(result)

    def _append_failed(self, report):
        result = self._new_result(report)
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
        result = self._new_result(report)
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
        result = self._new_result(report)
        result.execution.verdict = 'inconclusive'
        result.execution.note = f'{report.longrepr.reprcrash.message}\n' \
                                f'{report.longrepr.reprcrash.path}:{report.longrepr.reprcrash.lineno}'
        self.results.append(result)

    # pylint: disable=too-many-branches
    def _append_other(self, report):
        # For now, the only "other" the plugin give support is rerun
        self.rerun += 1
        result = self._new_result(report)
        result.execution.verdict = 'inconclusive'
        result.execution.note = 'rerun'
        self.results.append(result)

    # pylint: disable=too-many-statements
    def _new_result(self, report):
        result = Result(tcid=report.nodeid)
        result.execution.duration = report.duration
        result.execution.environment.framework.name = __pytest_info__.project_name
        result.execution.environment.framework.version = __pytest_info__.version
        result.execution.sut.commit_id = os.environ.get('GIT_COMMIT', "")
        result.execution.sut.branch = os.environ.get('GIT_BRANCH ', "")
        result.job.id = os.environ.get('BUILD_TAG', str(uuid.uuid1()))
        result.campaign = os.environ.get('JOB_NAME', "")
        result.execution.profiling = dict()
        if report.user_properties:
            result.execution.profiling['properties'] = dict()
        for (key, value) in report.user_properties:
            result.execution.profiling['properties'][key] = value
        if report.keywords:
            result.execution.profiling['keywords'] = []
        for key in report.keywords:
            result.execution.profiling['keywords'].append(key)
        dut = None
        for item in self.config.option.metadata:
            key, value = item

            # Dut
            if key.startswith('DUT') and not dut:
                dut = Dut()
                result.append_dut(dut)
            if key == 'DUT_SERIAL_NUMBER':
                dut.serial_number = value
                dut.type = 'hw'
            elif key == 'DUT_VERSION':
                dut.ver = value
            elif key == 'DUT_VENDOR':
                dut.vendor = value
            elif key == 'DUT_MODEL':
                dut.model = value
            elif key == 'DUT_PROVIDER':
                dut.provider = Provider()
                dut.provider.name = value

            # Sut
            elif key == 'SUT_COMPONENT':
                result.execution.sut.append_cut(value)
            elif key == 'SUT_FEATURE':
                result.execution.sut.append_fut(value)
            elif key == 'SUT_COMMIT_ID':
                result.execution.sut.commit_id = value

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

    def _link_session(self, session, result):  # pylint: disable=unused-argument
        # dut = Dut()
        # dut.serial_number = ''
        # result.append_dut(dut)

        result.execution.profiling['suite'] = dict(duration=self._suite_time_delta)
        result.execution.profiling['numtests'] = self._numtests
        result.execution.profiling['generated_at'] = self._generated.isoformat()

    def _upload_report(self, result: Result):
        try:
            self._client.post_result(result)
            self._uploaded_success += 1
        except Exception:  # pylint: disable=broad-except
            self._uploaded_failed += 1

    def _upload_reports(self, session):
        suite_stop_time = time.time()
        self._suite_time_delta = suite_stop_time - self.suite_start_time
        self._numtests = self.passed + self.failed + self.xpassed + self.xfailed
        self._generated = datetime.datetime.now()

        # pylint: disable=expression-not-assigned
        [self._link_session(session, result) for result in self.results]

        # pylint: disable=expression-not-assigned
        [print(result.data) for result in self.results]

        token = self.config.getoption("opentmi_token")
        try:
            self._client.login_with_access_token(token)

            num_cores = multiprocessing.cpu_count()
            Parallel(n_jobs=num_cores, backend='threading')\
                (delayed(self._upload_report)(result) for result in self.results)
        except Exception as error:  # pylint: disable=broad-except
            print(error)

    # pytest hooks

    def pytest_runtest_logreport(self, report):
        """
        logreport hook
        :param report: TestReport
        :return: None
        """
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
        """
        collect report hook
        :param report: TestReport
        :return: None
        """
        if report.failed:
            self._append_failed(report)

    # pylint: disable=unused-argument
    def pytest_sessionstart(self, session):
        """
        session start hook
        :param session: unused
        :return: None
        """
        self.suite_start_time = time.time()

    def pytest_sessionfinish(self, session):
        """
        session finish hook
        :param session:
        :return:
        """
        self._upload_reports(session)

    def pytest_terminal_summary(self, terminalreporter):
        """
        terminal summary hook
        :param terminalreporter:
        :return:
        """
        terminalreporter.write_sep("-", f"Uploaded {self._uploaded_success} "
                                        f"results successfully, {self._uploaded_failed} failed")

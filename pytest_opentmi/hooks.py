def pytest_opentmi_report_title(report):
    """ Called before adding the title to the report """

def pytest_opentmi_results_summary(prefix, summary, postfix):
    """ Called before adding the summary section to the report """

def pytest_opentmi_results_table_header(cells):
    """ Called after building results table header. """

def pytest_opentmi_results_table_row(report, cells):
    """ Called after building results table row. """

def pytest_opentmi_results_table_html(report, data):
    """ Called after building results table additional HTML. """

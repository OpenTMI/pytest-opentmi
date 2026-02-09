"""
pytest-opentmi
"""
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError


class _FrameworkInfo:
    """Simple container for framework information"""
    def __init__(self, project_name, pkg_version):
        self.project_name = project_name
        self.version = pkg_version


try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"

__pypi_url__ = "https://pypi.python.org/pypi/pytest-opentmi"
try:
    __pytest_info__ = _FrameworkInfo("pytest", version('pytest'))
except PackageNotFoundError:
    __pytest_info__ = _FrameworkInfo("pytest", "unknown")

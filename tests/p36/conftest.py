import sys


def pytest_ignore_collect():
    if sys.version_info < (3, 6):
        return True

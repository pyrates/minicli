from minicli import subparsers


def pytest_runtest_teardown():
    subparsers._choices_actions.clear()

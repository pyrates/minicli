from minicli import parser


def pytest_runtest_teardown():
    pass
    # Reset registered commands.
    # parser._subparsers._actions = []
    # for action in parser._actions:
    #     action.container._remove_action(action)
    # parser._actions = []

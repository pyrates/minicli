from minicli import registry, pre_hooks, post_hooks


def pytest_runtest_teardown():
    registry.clear()
    pre_hooks.clear()
    post_hooks.clear()

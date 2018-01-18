from minicli import _registry, _wrapper_functions, _wrapper_generators


def pytest_runtest_teardown():
    _registry.clear()
    _wrapper_functions.clear()
    _wrapper_generators.clear()

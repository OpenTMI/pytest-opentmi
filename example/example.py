import pytest


def setup_function(function):
    pass


def teardown_function(function):
    pass


def setup_module(module):
    #assert 0, 'oh no, setup module fails'
    pass

def teardown_module(module):
    pass


@pytest.mark.slow
def test_first_test():
    print('testing')


def test_second_test(record_property):
    record_property("example_key", 1)


def test_third_test():
    pass


@pytest.mark.skip(reason="no way of currently testing this")
def test_skip_marker():
    pass


def test_skip():
    pytest.skip("unsupported configuration")


@pytest.mark.xfail(reason='expected to fail')
def test_xfail():
    raise AssertionError('oh no')

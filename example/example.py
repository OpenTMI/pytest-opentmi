import pytest


def setup_function(function):
    pass


def teardown_function(function):
    pass


def setup_module(module):
    pass # assert 0, 'oh no, setup module fails'


def teardown_module(module):
    pass


def test_first_test():
    print('testing')


def test_second_test():
    pass


def test_third_test():
    pass


@pytest.mark.skip(reason="no way of currently testing this")
def test_skip_marker():
    pass


def test_skip():
    pytest.skip("unsupported configuration")

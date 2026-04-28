from typing import Union

_mock_module = None


def get_mock_module(config):
    """
    Import and return the actual "mock" module. By default this is
    "unittest.mock", but the user can force to always use "mock" using
    the mock_use_standalone_module ini option.
    """
    pass


def parse_ini_boolean(value: Union[bool, str]) -> bool:
    pass

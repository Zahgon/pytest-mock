import builtins
import functools
import inspect
import itertools
import unittest.mock
import warnings
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Optional
from typing import TypeVar
from typing import Union
from typing import cast
from typing import overload

import pytest

from ._util import get_mock_module
from ._util import parse_ini_boolean

_T = TypeVar("_T")

AsyncMockType = unittest.mock.AsyncMock
MockType = Union[
    unittest.mock.MagicMock,
    unittest.mock.AsyncMock,
    unittest.mock.NonCallableMagicMock,
]


class PytestMockWarning(UserWarning):
    """Base class for all warnings emitted by pytest-mock."""


@dataclass
class MockCacheItem:
    mock: MockType
    patch: Optional[Any] = None


@dataclass
class MockCache:
    """
    Cache MagicMock and Patcher instances so we can undo them later.
    """

    cache: list[MockCacheItem] = field(default_factory=list)

    def _find(self, mock: MockType) -> MockCacheItem:
        pass

    def add(self, mock: MockType, **kwargs: Any) -> MockCacheItem:
        pass

    def remove(self, mock: MockType) -> None:
        pass

    def clear(self) -> None:
        pass

    def __iter__(self) -> Iterator[MockCacheItem]:
        return iter(self.cache)


class MockerFixture:
    """
    Fixture that provides the same interface to functions in the mock module,
    ensuring that they are uninstalled at the end of each test.
    """

    def __init__(self, config: Any) -> None:
        self._mock_cache: MockCache = MockCache()
        self.mock_module = mock_module = get_mock_module(config)
        self.patch = self._Patcher(self._mock_cache, mock_module)  # type: MockerFixture._Patcher
        # aliases for convenience
        self.Mock = mock_module.Mock
        self.MagicMock = mock_module.MagicMock
        self.NonCallableMock = mock_module.NonCallableMock
        self.NonCallableMagicMock = mock_module.NonCallableMagicMock
        self.PropertyMock = mock_module.PropertyMock
        if hasattr(mock_module, "AsyncMock"):
            self.AsyncMock = mock_module.AsyncMock
        self.call = mock_module.call
        self.ANY = mock_module.ANY
        self.DEFAULT = mock_module.DEFAULT
        self.sentinel = mock_module.sentinel
        self.mock_open = mock_module.mock_open
        if hasattr(mock_module, "seal"):
            self.seal = mock_module.seal

    def create_autospec(
        self, spec: Any, spec_set: bool = False, instance: bool = False, **kwargs: Any
    ) -> MockType:
        pass

    def resetall(
        self, *, return_value: bool = False, side_effect: bool = False
    ) -> None:
        """
        Call reset_mock() on all patchers started by this fixture.

        :param bool return_value: Reset the return_value of mocks.
        :param bool side_effect: Reset the side_effect of mocks.
        """
        pass

    def stopall(self) -> None:
        """
        Stop all patchers started by this fixture. Can be safely called multiple
        times.
        """
        pass

    def stop(self, mock: unittest.mock.MagicMock) -> None:
        """
        Stops a previous patch or spy call by passing the ``MagicMock`` object
        returned by it.
        """
        pass

    def spy(
        self, obj: object, name: str, duplicate_iterators: bool = False
    ) -> MockType:
        """
        Create a spy of method. It will run method normally, but it is now
        possible to use `mock` call features with it, like call count.

        :param obj: An object.
        :param name: A method in object.
        :param duplicate_iterators: Whether to keep a copy of the returned iterator in `spy_return_iter`.
        :return: Spy object.
        """
        pass

    def stub(self, name: Optional[str] = None) -> unittest.mock.MagicMock:
        """
        Create a stub method. It accepts any arguments. Ideal to register to
        callbacks in tests.

        :param name: the constructed stub's name as used in repr
        :return: Stub object.
        """
        pass

    def async_stub(self, name: Optional[str] = None) -> AsyncMockType:
        """
        Create a async stub method. It accepts any arguments. Ideal to register to
        callbacks in tests.

        :param name: the constructed stub's name as used in repr
        :return: Stub object.
        """
        pass

    class _Patcher:
        """
        Object to provide the same interface as mock.patch, mock.patch.object,
        etc. We need this indirection to keep the same API of the mock package.
        """

        DEFAULT = object()

        def __init__(self, mock_cache, mock_module):
            self.__mock_cache = mock_cache
            self.mock_module = mock_module

        def _start_patch(
            self, mock_func: Any, warn_on_mock_enter: bool, *args: Any, **kwargs: Any
        ) -> MockType:
            """Patches something by calling the given function from the mock
            module, registering the patch to stop it later and returns the
            mock object resulting from the mock call.
            """
            pass

        def object(
            self,
            target: object,
            attribute: str,
            new: object = DEFAULT,
            spec: Optional[object] = None,
            create: bool = False,
            spec_set: Optional[object] = None,
            autospec: Optional[object] = None,
            new_callable: object = None,
            **kwargs: Any,
        ) -> MockType:
            """API to mock.patch.object"""
            pass

        def context_manager(
            self,
            target: builtins.object,
            attribute: str,
            new: builtins.object = DEFAULT,
            spec: Optional[builtins.object] = None,
            create: bool = False,
            spec_set: Optional[builtins.object] = None,
            autospec: Optional[builtins.object] = None,
            new_callable: builtins.object = None,
            **kwargs: Any,
        ) -> MockType:
            """This is equivalent to mock.patch.object except that the returned mock
            does not issue a warning when used as a context manager."""
            pass

        def multiple(
            self,
            target: builtins.object,
            spec: Optional[builtins.object] = None,
            create: bool = False,
            spec_set: Optional[builtins.object] = None,
            autospec: Optional[builtins.object] = None,
            new_callable: Optional[builtins.object] = None,
            **kwargs: Any,
        ) -> dict[str, MockType]:
            """API to mock.patch.multiple"""
            pass

        def dict(
            self,
            in_dict: Union[Mapping[Any, Any], str],
            values: Union[Mapping[Any, Any], Iterable[tuple[Any, Any]]] = (),
            clear: bool = False,
            **kwargs: Any,
        ) -> Any:
            """API to mock.patch.dict"""
            pass

        @overload
        def __call__(
            self,
            target: str,
            new: None = ...,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            new_callable: None = ...,
            **kwargs: Any,
        ) -> MockType: ...

        @overload
        def __call__(
            self,
            target: str,
            new: _T,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            new_callable: None = ...,
            **kwargs: Any,
        ) -> _T: ...

        @overload
        def __call__(
            self,
            target: str,
            new: None,
            spec: Optional[builtins.object],
            create: bool,
            spec_set: Optional[builtins.object],
            autospec: Optional[builtins.object],
            new_callable: Callable[[], _T],
            **kwargs: Any,
        ) -> _T: ...

        @overload
        def __call__(
            self,
            target: str,
            new: None = ...,
            spec: Optional[builtins.object] = ...,
            create: bool = ...,
            spec_set: Optional[builtins.object] = ...,
            autospec: Optional[builtins.object] = ...,
            *,
            new_callable: Callable[[], _T],
            **kwargs: Any,
        ) -> _T: ...

        def __call__(
            self,
            target: str,
            new: builtins.object = DEFAULT,
            spec: Optional[builtins.object] = None,
            create: bool = False,
            spec_set: Optional[builtins.object] = None,
            autospec: Optional[builtins.object] = None,
            new_callable: Optional[Callable[[], Any]] = None,
            **kwargs: Any,
        ) -> Any:
            """API to mock.patch"""
            if new is self.DEFAULT:
                new = self.mock_module.DEFAULT
            return self._start_patch(
                self.mock_module.patch,
                True,
                target,
                new=new,
                spec=spec,
                create=create,
                spec_set=spec_set,
                autospec=autospec,
                new_callable=new_callable,
                **kwargs,
            )


def _mocker(pytestconfig: Any) -> Generator[MockerFixture, None, None]:
    """
    Return an object that has the same interface to the `mock` module, but
    takes care of automatically undoing all patches after each test method.
    """
    pass


mocker = pytest.fixture()(_mocker)  # default scope is function
class_mocker = pytest.fixture(scope="class")(_mocker)
module_mocker = pytest.fixture(scope="module")(_mocker)
package_mocker = pytest.fixture(scope="package")(_mocker)
session_mocker = pytest.fixture(scope="session")(_mocker)


_mock_module_patches: list[Any] = []
_mock_module_originals: dict[str, Any] = {}


def assert_wrapper(
    __wrapped_mock_method__: Callable[..., Any], *args: Any, **kwargs: Any
) -> None:
    pass


def assert_has_calls_wrapper(
    __wrapped_mock_method__: Callable[..., Any], *args: Any, **kwargs: Any
) -> None:
    pass


def wrap_assert_not_called(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_called_with(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_called_once(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_called_once_with(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_has_calls(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_any_call(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_called(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_not_awaited(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_awaited_with(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_awaited_once(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_awaited_once_with(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_has_awaits(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_any_await(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_awaited(*args: Any, **kwargs: Any) -> None:
    pass


def wrap_assert_methods(config: Any) -> None:
    """
    Wrap assert methods of mock module so we can hide their traceback and
    add introspection information to specified argument asserts.
    """
    pass


def unwrap_assert_methods() -> None:
    pass


def pytest_addoption(parser: Any) -> None:
    pass


def pytest_configure(config: Any) -> None:
    pass

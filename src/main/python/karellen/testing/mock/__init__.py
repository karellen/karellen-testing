#
#  -*- coding: utf-8 -*-
#
# (C) Copyright 2016 Karellen, Inc. (http://karellen.co/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import types

from unittest.mock import patch, Mock, NonCallableMock, DEFAULT, _all_magics, _calculate_return_value

__all__ = ["Spy", "MagicSpy", "instrument_wrapped_magic"]


class Spy(object):
    """
        This Spy allows Mock to account for all the calls to the methods of the object wrapped by Mock or MagicMock.

        Ordinarily once the wrapped call enters the wrapped object, the "self" reference is to the original wrapped
        object, not the mock. Any calls to other methods of the object will be through the wrapped object and not the
        mock and therefore forgo any tracking by the mock and prevent you from verifying API contracts with
        "assert_called_..." methods.

        Spy rewrites the bounding for all the object methods to ensure that the self object passed to the
        method calls is the Spy itself. This allows Spy to intercept all other internal calls to methods of self and
        invoke them through the wrapping Mock completing the spying loop and allowing Mock to account for all wrapped
        calls.

        Obviously, Spy, being "self" in every method call, must provide for field access (get and set), which are also
        passed through this spy and are delegated as appropriate.
    """

    def __new__(cls, *args, **kw):
        # every instance has its own class
        # so we can create magic methods on the
        # class without stomping on other mocks
        new = type(cls.__name__, (cls,), {'__doc__': cls.__doc__})
        instance = object.__new__(new)
        return instance

    def __init__(self, mock):
        self.__dict__["_Spy__mock"] = mock

    def __getattribute__(self, item: str):
        if item == "__dict__" or item.startswith("_Spy"):
            return super().__getattribute__(item)

        attr = getattr(self.__mock, item)

        if isinstance(attr, NonCallableMock):
            mock_wraps = attr._mock_wraps
            wrapped = self.__mock._mock_wraps
            if mock_wraps is not None:
                # Is the wrapped value present?
                if hasattr(mock_wraps, "__self__"):
                    # Is the wrapped value a method?
                    attr_self = mock_wraps.__self__
                    if attr_self is not self and not isinstance(attr_self, type):
                        # If the method belongs to a Mock and not rebound to the Spy and method is not class method
                        if hasattr(mock_wraps, "__func__"):
                            # If this method is not a method-wrapper
                            # Rebind mock method to use this Spy as self
                            # This will allow self.method() to go back into the spy and into the Mock to be tracked
                            setattr_internal(attr, "_mock_wraps", types.MethodType(mock_wraps.__func__, self))
                        else:
                            # This is a method-wrapper that has no function object and has to be proxied
                            setattr_internal(attr, "_mock_wraps",
                                             types.MethodType(
                                                 make_method_wrapper_closure(type(wrapped), self, mock_wraps.__name__),
                                                 self))
                else:
                    # This attribute is not a wrapped method
                    if not isinstance(mock_wraps, types.FunctionType) and hasattr(wrapped, item):
                        # If wrapped is not a function (e.g. static method) and the underlying wrapped
                        # has this attribute then simply return the value of that attribute directly
                        return getattr(wrapped, item)
            else:
                if attr._mock_return_value is DEFAULT and hasattr(wrapped, item) and \
                        getattr(wrapped, item) is None:
                    # This attribute is not wrapped, and if it doesn't have a return value
                    # and is None then just return None
                    return None

        # In all other cases we return the attribute as we found it
        return attr

    def __setattr__(self, key: str, value):
        mock = self.__mock
        try:
            attr = getattr(mock, key)
            mock_wraps = attr._mock_wraps
            wrapped = mock._mock_wraps
            if mock_wraps is None or \
                    isinstance(mock_wraps, types.MethodType) and mock_wraps.__self__ in (self, wrapped):
                # If attribute is not wrapped or is a method of the wrapped object and method is bound
                # to Spy or spied mock then delegate to Mock
                return setattr_internal(mock, key, value)

            # Otherwise set the value directly on the object that is wrapped and is spied on
            setattr_internal(wrapped, key, value)
        except AttributeError:
            # If Mock doesn't have this attribute delegate to Mock
            return setattr_internal(mock, key, value)


def get_proper_attr_target(obj, key):
    if not isinstance(obj, type) and key.startswith("__"):
        return type(obj)
    return obj


def setattr_internal(obj, key, value):
    return setattr(get_proper_attr_target(obj, key), key, value)


def make_method_closure(method):
    def spy_proxy_mock(self, *args, **kwargs):
        return getattr(self, method)(*args, **kwargs)

    return spy_proxy_mock


def make_method_wrapper_closure(cls, obj, method_wrapper):
    def method_wrapper_proxy(self, *args, **kwargs):
        return getattr(cls, method_wrapper)(obj, *args, **kwargs)

    return method_wrapper_proxy


_magics = sorted(_all_magics)

_method_wrapper_type = type(object.__str__)


def instrument_wrapped_magic(wrapped, mock, spy):
    with patch.dict(_calculate_return_value, {}, clear=True):
        for magic in _magics:
            do_wrap_magic = False
            do_proxy_mock = False
            if hasattr(wrapped, magic):
                wrapped_method = getattr(wrapped, magic)
                with patch("unittest.mock.MagicProxy.create_mock", return_value=None):
                    mock_method = getattr(mock, magic)
                if mock_method is None or not isinstance(mock_method, NonCallableMock):
                    do_wrap_magic = True
                else:
                    do_proxy_mock = True
                    if mock_method._mock_wraps is None and mock_method._mock_return_value is DEFAULT:
                        do_wrap_magic = True

            if do_wrap_magic:
                do_proxy_mock = True
                setattr_internal(mock, magic, type(mock)(wraps=wrapped_method, name=str(wrapped_method)))

            if do_proxy_mock:
                setattr_internal(spy, magic, types.MethodType(make_method_closure(magic), spy))


def magic_spy(wrapped, wrap_magic=True, mock_type=Mock):
    mock = mock_type(spec_set=wrapped, wraps=wrapped)
    spy = Spy(mock)
    if wrap_magic:
        instrument_wrapped_magic(wrapped, mock, spy)
    return spy


MagicSpy = magic_spy

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

from unittest.mock import MagicMock, DEFAULT

__all__ = ["Spy", "MagicSpy"]


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
        passed through the
    """

    def __init__(self, mock):
        self.__dict__["_%s__mock" % self.__class__.__name__] = mock
        self.__dict__["_%s__wrapped" % self.__class__.__name__] = self.__mock._mock_wraps

    def __getattr__(self, item):
        attr = getattr(self.__mock, item)

        mock_wraps = attr._mock_wraps
        if mock_wraps is not None:
            # Is the wrapped value present?
            if isinstance(mock_wraps, types.MethodType):
                # Is the wrapped value a method?
                attr_self = mock_wraps.__self__
                if attr_self is not self and not isinstance(attr_self, type):
                    # If the method belongs to a Mock and method is not class method
                    # Rebind mock method to use this Spy as self
                    # This will allow self.method() to go back into the spy and into the Mock to be tracked
                    attr._mock_wraps = types.MethodType(attr._mock_wraps.__func__, self)
            else:
                # This attribute is not a method
                if not isinstance(mock_wraps, types.FunctionType) and hasattr(self.__wrapped, item):
                    # If wrapped is not a function (e.g. static method) and the underlying wrapped
                    # has this attribute then simply return the value of that attribute directly
                    return getattr(self.__wrapped, item)
        else:
            if attr._mock_return_value is DEFAULT and hasattr(self.__wrapped, item) and getattr(self.__wrapped,
                                                                                                item) is None:
                # This attribute is not wrapped, and if it doesn't have a return value
                # and is None then just return None
                return None

        # In all other cases we return the attribute as we found it
        return attr

    def __setattr__(self, key: str, value):
        try:
            attr = getattr(self.__mock, key)
            mock_wraps = attr._mock_wraps
            if mock_wraps is None or \
                    isinstance(mock_wraps, types.MethodType) and mock_wraps.__self__ in (self, self.__wrapped):
                # If attribute is not wrapped or is a method of the wrapped object and method is bound
                # to Spy or spied mock then delegate to Mock
                return setattr(self.__mock, key, value)

            # Otherwise set the value directly on the object that is wrapped and is spied on
            setattr(self.__wrapped, key, value)
        except AttributeError:
            # If Mock doesn't have this attribute delegate to Mock
            return setattr(self.__mock, key, value)


def magic_spy(obj):
    return Spy(MagicMock(spec_set=obj, wraps=obj))


MagicSpy = magic_spy

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

import warnings
from unittest import TestCase
from unittest.mock import MagicMock, NonCallableMock

from karellen.testing.mock import MagicSpy, Spy, instrument_wrapped_magic

warnings.simplefilter('always')


class TestSpy(TestCase):
    class Class_A(object):
        def __init__(self):
            self.value = 10
            self.none_value = None

        def method_X(self):
            assert self.value == 10
            self.method_Y()

        def method_Y(self):
            self.value = 9

        @staticmethod
        def foo():
            pass

        @classmethod
        def bar(cls):
            pass

        def __repr__(self):
            return "Class_A repr"

    def test_magic_spy(self):
        mock = MagicSpy(TestSpy.Class_A())

        mock.__repr__.assert_not_called()
        self.assertEqual("Class_A repr", repr(mock))
        mock.__repr__.assert_called_once_with()

        self.assertIsInstance(mock, TestSpy.Class_A)
        mock.foo()
        mock.bar()
        self.assertEqual("Class_A repr", str(mock))
        mock.__str__.assert_called_once_with()
        self.assertEqual(mock.__repr__.call_count, 2)

        mock.method_X()
        mock.method_Y.assert_called_once_with()
        mock.foo.assert_called_once_with()
        mock.bar.assert_called_once_with()

        self.assertEqual(mock.value, 9)
        self.assertIsNone(mock.none_value)

    def test_spy_unwrapped(self):
        mock = Spy(MagicMock(TestSpy.Class_A()))
        mock.method_X()
        mock.method_Y.assert_not_called()
        mock.bazinga = MagicMock()

    def test_spy_unspecced(self):
        mock = Spy(MagicMock())
        mock.method_X()
        mock.method_Y.assert_not_called()
        mock.bazinga = MagicMock()

    def test_spy_substituted_magic_method(self):
        wrapped = TestSpy.Class_A()
        wrapped.__get__ = lambda *args, **kwargs: None

        def mocked_repr():
            return "Mocked repr"

        def mocked_str(self):
            return "Mocked str"

        mock_proper = MagicMock(wraps=wrapped)
        mock_proper.__str__ = mocked_str
        mock_proper.__repr__ = MagicMock(spec_set=mocked_str, wraps=mocked_repr)
        get_mock = MagicMock()
        mock_proper.__get__ = get_mock
        mock = Spy(mock_proper)
        instrument_wrapped_magic(wrapped, mock_proper, mock)

        mock.method_X()
        mock.method_Y.assert_called_once_with()
        self.assertEqual("Mocked str", str(mock))
        self.assertEqual("Mocked repr", repr(mock))
        self.assertIs(mock.__get__, get_mock)

    def test_spy_no_wrapped_magic(self):
        mock = MagicSpy(TestSpy.Class_A(), wrap_magic=False)
        self.assertNotEqual("Class_A repr", repr(mock))
        self.assertNotEqual("Class_A repr", str(mock))
        self.assertNotIsInstance(mock.__str__, NonCallableMock)

    def test_spy_wrapped_magic_with_magicmock(self):
        mock = MagicSpy(TestSpy.Class_A(), mock_type=MagicMock)
        self.assertEqual("Class_A repr", repr(mock))
        mock.__repr__.assert_called_once_with()
        self.assertEqual("Class_A repr", str(mock))
        mock.__str__.assert_called_once_with()
        self.assertIsInstance(mock.__str__, NonCallableMock)

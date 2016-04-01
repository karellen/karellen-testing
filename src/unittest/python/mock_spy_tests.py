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

from unittest import TestCase
from unittest.mock import MagicMock

from karellen.testing.mock import MagicSpy, Spy


class TestSpy(TestCase):
    class Class_A(object):
        def __init__(self):
            self.value = 10
            self.none_value = None

        def method_X(self):
            assert self.value == 10
            print(self.value)
            self.method_Y()

        def method_Y(self):
            self.value = 9

        @staticmethod
        def foo():
            print("foo")

        @classmethod
        def bar(cls):
            print("bar: " + str(cls))

    def test_magic_spy(self):
        mock = MagicSpy(TestSpy.Class_A())

        mock.foo()
        mock.bar()
        mock.method_X()

        mock.method_Y.assert_called_once_with()
        mock.foo.assert_called_once_with()
        mock.bar.assert_called_once_with()

        self.assertEquals(mock.value, 9)
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

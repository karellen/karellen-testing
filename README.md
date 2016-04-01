# Karellen Testing Frameworks and Utilities
Karellen Testing Frameworks and Utilities

## Mock
A collection of Mock utilities helping with common tasks

### Spy

```python
from unittest import TestCase
from karellen.testing.mock import MagicSpy


class Class_A(object):
    def method_X(self):
        self.method_Y()

    def method_Y(self):
        pass


class TestSpy(TestCase):
    def test_class_a_api(self):
        mock = MagicSpy(Class_A())

        mock.method_X()
        mock.method_Y.assert_called_once_with()
```
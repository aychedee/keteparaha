from unittest import TestCase

from keteparaha.flow import ignore, retry


class IgnoreTest(TestCase):

    def test_ignores_provided_errors(self):
        a, k = (1, 2, 3), {'1': 1, '2': 2, '3': 3}
        def test_func(*args, **kwargs):
            return args, kwargs

        wrapped = ignore(test_func, (TypeError, KeyError))

        self.assertEqual((wrapped(*a, **k)), (a, k))

    def test_does_ignore_other_errors(self):
        a, k = (1, 2, 3), {'1': 1, '2': 2, '3': 3}
        def test_func(*args, **kwargs):
            raise RuntimeError()

        wrapped = ignore(test_func, (TypeError, KeyError))

        with self.assertRaises(RuntimeError):
            wrapped(*a, **k)

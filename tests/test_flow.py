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


class RetryTest(TestCase):

    def test_retries_function_given_number_of_times(self):
        a, k = (1, 2, 3), {'1': 1, '2': 2, '3': 3}

        globals()['counter'] = 5

        def test_func(*args, **kwargs):
            global counter
            if counter > 0:
                counter -= 1
                raise Exception()
            return args, kwargs

        wrapped = retry(test_func, (Exception), attempts=6)

        self.assertEqual((wrapped(*a, **k)), (a, k))

    def test_raises_error_if_function_still_erroring(self):
        a, k = (1, 2, 3), {'1': 1, '2': 2, '3': 3}

        globals()['counter'] = 5

        def test_func(*args, **kwargs):
            global counter
            if counter > 0:
                counter -= 1
                raise Exception()
            return args, kwargs

        wrapped = retry(test_func, (Exception), attempts=5)

        with self.assertRaises(Exception):
            wrapped(*a, **k)

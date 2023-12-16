import sys
import traceback
import unittest

from l10n_traceback.error import iter_tbs


class TestError(unittest.TestCase):
    def test_iter_tbs(self):
        try:
            1 / 0  # type:ignore
        except Exception:
            tbs = iter_tbs(traceback.format_exception(*sys.exc_info()))
            self.assertEqual((len([*tbs])), 3)

        try:
            try:  # sourcery skip: raise-from-previous-error
                raise RuntimeError("test\n\n")
            except Exception:
                raise RuntimeError("\n\ntest")
        except Exception:
            tbs = iter_tbs(traceback.format_exception(*sys.exc_info()))
            self.assertEqual((len([*tbs])), 7)

        try:
            try:
                raise RuntimeError("test\n\n")
            except Exception as e:
                raise RuntimeError("\n\ntest") from e
        except Exception:
            tbs = iter_tbs(traceback.format_exception(*sys.exc_info()))
            self.assertEqual((len([*tbs])), 7)

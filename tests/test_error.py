import sys
import traceback
import unittest

from l10n_traceback.error import iter_tbs


class TestError(unittest.TestCase):
    def test_iter_tbs(self):
        try:
            1 / 0  # type:ignore
        except:
            tbs = iter_tbs(traceback.format_exception(*sys.exc_info()))
            self.assertEqual((len([*tbs])), 3)

        try:
            try:
                raise Exception("test\n\n")
            except Exception:
                raise Exception("\n\ntest")
        except:
            tbs = iter_tbs(traceback.format_exception(*sys.exc_info()))
            self.assertEqual((len([*tbs])), 7)

        try:
            try:
                raise Exception("test\n\n")
            except Exception as e:
                raise Exception("\n\ntest") from e
        except:
            tbs = iter_tbs(traceback.format_exception(*sys.exc_info()))
            self.assertEqual((len([*tbs])), 7)

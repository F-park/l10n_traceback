import sys

from .error import except_hook

sys.excepthook = except_hook

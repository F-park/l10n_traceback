from enum import Enum


class Color(str, Enum):
    RED = "\033[31m%s\033[0m"
    GREEN = "\033[32m%s\033[0m"
    YELLOW = "\033[33m%s\033[0m"
    BLUE = "\033[34m%s\033[0m"

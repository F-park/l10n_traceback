import sys
import traceback
from functools import partial
from types import TracebackType
from typing import Optional

from .color import Color

print_error = partial(print, file=sys.stderr)

texts = {
    "traceback": "Traceback (most recent call last):\n",
    "another": "\nDuring handling of the above exception, another exception occurred:\n\n",
    "from": "\nThe above exception was the direct cause of the following exception:\n\n",
}


def except_hook(
    e_type: "type[BaseException]", e_value: BaseException, e_traceback: "TracebackType | None"
):
    if e_type == ExceptionGroup:
        # TODO support Traceback group

        traceback.print_exception(e_type, e_value, e_traceback)
        return

    try:
        _except_hook(e_type, e_value, e_traceback)
    except Exception:
        traceback.print_exc()


def iter_tbs(tbs: "list[str]"):
    tbs_iter = iter(tbs)
    s = ""
    while True:
        try:
            line = next(tbs_iter)
            if line in texts.values():
                yield line
                continue

            if ": " in line.strip():
                if s:
                    yield s
                    yield line
                    s = ""
                else:
                    s += line
            elif line.strip().startswith("File ") and s:
                yield s
                s = ""
            else:
                s += line
        except StopIteration:
            return


def _except_hook(
    e_type: "type[BaseException]", e_value: BaseException, e_traceback: "TracebackType | None"
):
    tbs = traceback.format_exception(e_type, e_value, e_traceback)
    for line in iter_tbs(tbs):
        if line == texts["traceback"]:
            print_error(Color.RED % "错误回溯")
        elif line.lstrip().startswith("File "):
            handle_file(*line.split(", ", maxsplit=2))
        elif ": " in line.strip():
            exception, _, message = line.partition(":")
            handle_exception(exception, message)
        elif line == texts["another"]:
            print_error(Color.RED % "\n在处理上述异常的过程中, 发生了另一个异常:\n\n")
        elif line == texts["from"]:
            print_error(Color.RED % "\n上述异常是以下异常的直接原因:\n\n")


def handle_exception(exception: str, message: str):
    def e_is_prefix(old_prefix: str, new_prefix: str):
        # python > 3.9 can use str.removeprefix
        nonlocal exception
        if exception.startswith(old_prefix):
            exception = new_prefix + exception[len(old_prefix) :]
            return True
        return False

    def e_is_suffix(old_suffix: str, new_suffix: str):
        # python > 3.9 can use str.removesuffix
        nonlocal exception
        if exception.endswith(old_suffix):
            exception = exception[: -len(old_suffix)] + new_suffix
            return True
        return False

    def m_is_prefix(old_prefix: str, new_prefix: str):
        # python > 3.9 can use str.removeprefix
        nonlocal message
        if message.startswith(" " + old_prefix):
            message = f" {new_prefix}{message[len(old_prefix)+1 :]}"
            return True
        return False

    def m_is_suffix(old_suffix: str, new_suffix: str):
        # python > 3.9 can use str.removesuffix
        nonlocal message
        if message.endswith(old_suffix + "\n"):
            message = f"{message[ : -len(old_suffix)-1]}{new_suffix}\n"
            return True
        return False

    if exception == "SyntaxError":
        if m_is_prefix("invalid syntax", "不合法"):
            m_is_suffix("Perhaps you forgot a comma?", "可能你忘了逗号?")
    elif exception == "NameError":
        if m_is_prefix("name", "名"):
            m_is_suffix("is not defined", "未定义")
    elif exception == "AttributeError":
        message = message.replace("object has no attribute", "对象没有属性")
    elif exception == "IndentationError":
        m_is_prefix("unexpected indent", "意外的缩进")
    elif exception == "ZeroDivisionError":
        m_is_prefix("division by zero", "除数为零")

    if e_is_suffix("Exception", "异常"):
        pass
    elif e_is_suffix("Error", "错误"):
        pass
    elif e_is_suffix("Warning", "警告"):
        pass

    if e_is_prefix("Syntax", "语法"):
        pass
    elif e_is_prefix("Name", "名字"):
        pass
    elif e_is_prefix("Type", "类型"):
        pass
    elif e_is_prefix("Attribute", "属性"):
        pass
    elif e_is_prefix("Indentation", "缩进"):
        pass
    elif e_is_prefix("UnboundLocal", "局部变量未初始化"):
        pass
    elif e_is_prefix("Runtime", "运行时"):
        pass
    elif e_is_prefix("NotImplemented", "未实现"):
        pass
    elif e_is_prefix("Assertion", "断言"):
        pass
    elif e_is_prefix("ZeroDivision", "零除"):
        pass

    print(f"{exception}:{message}")


def handle_file(file_str: str, line_str: str, module_str: Optional[str] = None):
    if module_str is None:
        line_str, _, module_str = line_str.partition("\n")
        module_str = "\n" + module_str

    file_str_parts = list(file_str.partition("File "))
    if file_str_parts[2] == '"<stdin>"' and not module_str.startswith("\n"):
        return
    file_str_parts[1] = Color.YELLOW % "在文件"
    file_str = "".join(file_str_parts)

    line_str_parts = list(line_str.partition("line "))
    line_str_parts[1] = Color.BLUE % "第"
    line_str_parts.append(Color.BLUE % "行")
    line_str = "".join(line_str_parts)

    module_str_parts = list(module_str.partition("in "))
    if module_str_parts[1]:
        module_str_parts[1] = ""

        _ = list(module_str_parts[2].partition("\n"))
        _[0] = _[0] + Color.GREEN % "中"
        module_str_parts[2] = "".join(_)

    module_str = "".join(module_str_parts)

    print_error(f"{file_str}, {line_str}{',' if module_str_parts[1] else ''} {module_str}")

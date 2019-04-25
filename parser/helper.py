import re


def find_between(s: str, first: str, last: str):
    """Gives you the first thing between the two delimiters
    """
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end], end
    except ValueError:
        return "", -1


def remove_indent(string):
    i = 0
    while i < len(string) and string[i] == ' ' or string[i] == '\t':
        i += 1
    return string[i:]


reg_function = re.compile(r"([^,]+\(.+?\))")


def is_function_call(string):
    return len(reg_function.findall(string)) > 0, string.split('(')[0]


def infere_type(var):
    for assignment in var.assignment:
        pass
    return 'int'


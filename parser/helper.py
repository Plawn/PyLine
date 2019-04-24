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
    while string[i] == ' ' or string[i] == '\t':
        i += 1
    return string[i:]
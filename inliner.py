class Scope:
    def __init__(self, *args, **kwargs):
        pass

class Variable:
    def __init__(self, *args, **kwargs):
        pass


class Line:
    def __init__(self, *args, **kwargs):
        pass

class Func:
    def __init__(self, text, *args, **kwargs):
        self.text = text
    def __repr__(self):
        return self.text


def get_indent_lvl(line:str, indent:str):
    i = 0
    for c in line:
        if c == indent:
            i += 1
        else:
            break
    return i
    


def find_funcs(filename):
    with open(filename, 'r') as f: 
        lines = f.readlines()
    


def parse_func():
    pass


def should_be_inlined():
    pass
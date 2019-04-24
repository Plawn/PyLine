import os
from typing import List, Dict, Tuple
from .helper import find_between
from . import helper


SPACE = 'space'
CHAR_SPACE = ' '
CHAR_TAB = '    '


TYPE_ANY = 'any'

SCOPES = {

}


# Placeholder for now
class Indent:
    def __init__(self):
        self.type = SPACE
        self.length = 4
        self.char = CHAR_SPACE


class Scope:
    def __init__(self, parent, name='', *args, **kwargs):
        self.symbols: Dict[str:Variable] = {}
        self.name = name
        self.parent = parent
    def get(self, symbol: str):
        return self.symbols[symbol]

    def add(self, symbol):
        self.symbols[symbol.symbol] = symbol

    def __repr__(self):
        return '<Scope {} : {}>'.format(self.name, self.parent)

    def wrap_childs(self):
        for s  in self.symbols:
            self.symbols[s] = self.symbols[s].add_prefix(self.name)

class Variable:
    def __init__(self, symbol, type=TYPE_ANY,*args, **kwargs):
        self.symbol = symbol
        self.type = type
        self.has_type = True if self.type != TYPE_ANY else False

    def __repr__(self):
        return '<Var {}:{}>'.format(self.symbol, self.type)

    def __eq__(self, other):
        return self.symbol == other.symbol

    def add_prefix(self, pre:str):
        self.symbol = pre + self.symbol

def get_variables_left(member:str):
    return [Variable(s) for s in map( lambda x:x.strip(), member.split(','))]

def get_call_right(member:str):
    a = map(member.split(','), lambda x:x.strip())

class Line:
    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.comment = ''
        self.is_assign = False
        self.vars = []
        self.left_member: Dict[str, Variable] = {}
        self.left_var = []

        self.right_member = {}
        self.parse()
    def rebuild(self):
        if self.is_assign :
            self.text = self.left_member + '=' +self.right_member
        else:
            pass


    def __repr__(self):
        return '<Line {}>'.format(self.text)

    def parse_variable(self):
        text = helper.remove_indent(self.text)
        i = 0
        if text[0:4] == 'while':
            result = process_while(text)
        while i < len(text):
            char = text[i]
            if char == '=':
                print('got an assignment')
                self.is_assign = True
                
                self.left_member = text[:i]
                var_list = [Variable(i.strip()) for i in self.left_member.split(',')]
                self.right_member = text[i:]
                self.left_var = get_variables_left(self.left_member)
                break
                # it's an assigment
            i += 1



    def __iter__(self):
        for var in self.vars:
            yield var

    def parse(self):
        self.parse_variable()
        self.text, self.comment = remove_comment(self.text)

    def get_variables(self):
        pass


class Func:
    def __init__(self, parent,text='',*args, **kwargs):
        self.text = text
        self.nested = False
        self.lines = {}
        self._need_rebuild = True
        self.args: List[Variable] = []
        self.def_line = None
        self.nested_funcs = {}
        self.name = ''
        self.last_place = 0
        self.needs_inline = False
        self.function_calls = {}
        self.scope = Scope(parent, self.name)

    def build(self):
        self.text = ''
        for i in range(self.last_place):
            if i in self.lines:
                self.text += self.lines[i].text + '\n'
            elif i in self.nested_funcs:
                self.text += str(self.nested_funcs[i]) + '\n'

    def __repr__(self):
        if self._need_rebuild:
            self.build()
        return self.text
    def set_rebuild(self):
        self._need_rebuild = True

    def add_def_line(self, line):
        self.set_rebuild()
        self.lines[0] = line
        self.last_place = 1
        self.def_line = line

    def append_line(self, line):
        self._need_rebuild = True
        self.lines[self.last_place] = line
        self.last_place += 1

    def parse_def_line(self):
        self.name = self.def_line.text.split('(')[0].replace('def', '').strip()
        _, comment = remove_comment(self.def_line)
        if 'inline' in comment:
            self.needs_inline = True
        args = find_between(self.def_line.text, '(', ')')[0].split(',')
        self.args = []
        for arg in args:
            t = arg.split(':')
            typ = TYPE_ANY
            if len(t) > 1:
                typ = t[1]
            self.args.append(Variable(t[0], type=typ))

    def add_nested_func(self, func):
        self.nested_funcs[self.last_place] = func
        self.last_place += 1

    def replace_func_with_inlined(self, func):
        pass


def remove_trailing_char(text: str, i_type: str):
    t, i = text[::-1], 0
    while i < len(text) and t[i] == i_type:
        i += 1
    return text[:len(text)-i]

def process_while(text):
    return text


def remove_comment(line: str):
    try:
        i = line.index('#')
        return line[:i], line[i:]
    except:
        return line, ''


def indent_lvl(line: str, indent: Indent):
    if indent.type == SPACE:
        if line[:indent.length] == SPACE * indent.length:
            return 1
        line = remove_trailing_char(line.split('=')[0], indent.char)
        i = 0
        while i < len(line) and line[i] == ' ':
            i += 1
        return i / indent.length
    else:
        pass


def get_indent_char(text: str):
    # placeholder for now
    return Indent()


def find_no_err(s: str, sub: str):
    try:
        return s.index(sub)
    except:
        return -1


def should_make_func(line: str):
    if 'def' in line:
        i = find_no_err(line, '#')
        if i == -1 or (i >= 0 and line.index('def') < i):
            return True
    return False


def get_func(lines: str, indent_char: str, i: int, parent_scope:Scope):
    f = Func(parent_scope)
    f.add_def_line(Line(lines[i]))
    f.parse_def_line()
    indent = indent_lvl(lines[i], indent_char)
    i += 1
    while indent_lvl(lines[i], indent_char) > indent and i < len(lines):
        if should_make_func(lines[i]):
            f1, i = get_func(lines[i:], indent_char, i-1, f.scope)
            f.add_nested_func(f1)
        else:
            f.append_line(Line(lines[i]))
        i += 1
    return f, i


def find_funcs(text: str):
    lines = text.split('\n')
    i = 0
    indent_char = get_indent_char(text)
    funcs = []
    while i < len(lines):
        if should_make_func(lines[i]):
            f, i = get_func(lines, indent_char, i, Scope(None, 'main'))
            funcs.append(f)
        i += 1
    return funcs


def parse_func():
    pass


def should_be_inlined():
    pass

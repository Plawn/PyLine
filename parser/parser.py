import os
from typing import List, Dict, Tuple
from .helper import find_between
from . import helper


SPACE = 'space'
CHAR_SPACE = ' '
CHAR_TAB = '    '
UNKNOW_INDENT = 'unknow indent'

TYPE_ANY = 'any'



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

    def add(self, *symbols):
        for symbol in symbols : 
            self.symbols[symbol.symbol] = symbol

    def __repr__(self):
        return '<Scope {} : {}>'.format(self.name, self.parent)

    def wrap_childs(self):
        for _, symbol in self.symbols.items():
            symbol.set_prefix(self.name+'_')


class Variable:
    def __init__(self, symbol, assigments=[], *args, **kwargs):
        self.symbol = None
        self._symbol = None
        self.prefix = ''
        self.build_symbol(symbol)
        self.has_type = True if self.type != TYPE_ANY else False
        self.assigments = assigments
        
    
    def build_symbol(self, symbol=None):
        if symbol is not None:
            s = symbol.split(':')
            self.symbol = self.prefix + s[0]
            self._symbol = self.symbol
            self.type = TYPE_ANY if len(s) < 2 else s[1]
        else:
            self.symbol = self.prefix + self._symbol
    def __repr__(self):
        return '<Var {}:{}>'.format(self.symbol, self.type)

    def __eq__(self, other):
        return self.symbol == other.symbol

    def set_prefix(self, pre: str):
        self.prefix = pre
        self.build_symbol()



def get_variables_left(member: str):
    return [Variable(s) for s in map(lambda x:x.strip(), member.split(','))]


def get_call_right(member: str):
    a = map(member.split(','), lambda x: x.strip())


class Line:
    def __init__(self, text, _indent_lvl=UNKNOW_INDENT, no_parse=False, *args, **kwargs):
        self.text = text
        self.comment = ''
        self.is_assign = False
        self.vars = []
        self.left_member: Dict[str, Variable] = {}
        self.left_var = []

        self.indent_type = Indent()
        self.right_member = {}
        self.unindented = helper.remove_indent(self.text)
        self.indent_lvl = _indent_lvl if _indent_lvl != UNKNOW_INDENT else indent_lvl(
            self.text, self.indent_type)
        if _indent_lvl != UNKNOW_INDENT:
            self.setup_indent()

        self.is_return_line = False
        self.sublines = [self]
        if not no_parse:
            self.parse()

    def _is_return_line(self):
        return self.unindented[:6] == 'return'

    def setup_indent(self):
        self.text = self.indent_type.char * self.indent_lvl * \
            self.indent_type.length + self.text

    def make_easier_return(self):
        self.sublines = []
        self.sublines.append(Line('_ = {}'.format(self.unindented[6:]), self.indent_lvl))
        self.sublines.append(Line('return _', self.indent_lvl, no_parse=True))

    def rebuild(self):
        if self.is_assign:
            self.text = ', '.join(var.symbol for var in self.left_var)
            self.text += '=' + self.right_member
            self.setup_indent()
        elif self.is_return_line:
            self.text = ''
            for line in self.sublines:
                self.text += line.text + '\n'

    def __repr__(self):
        return '<Line {}>'.format(self.text)

    def parse_variable(self):
        text = helper.remove_indent(self.text)

        if text[:4] == 'while':
            result = process_while(text)
            return
        elif text[:3] == 'for':
            result = process_for(text)
            return
        elif text[:4] == 'with':
            result = process_with(text)
            return
        elif self._is_return_line():
            self.is_return_line = True
            self.make_easier_return()
        i = 1
        while i < len(text):
            char = text[i]
            if text[i] == '=' and text[i-1] != '=' and text[i+1] != '=':
                print('got an assignment')
                self.is_assign = True

                self.left_member = text[:i].strip()
                self.left_var = get_variables_left(self.left_member)
                print(text, self.left_var)

                self.right_member = text[i+1:].strip()
                right_var = []
                for temp in self.right_member.split(','):
                    is_func_call, func_name = helper.is_function_call(
                        temp)
                    if is_func_call :
                        # actually the hard part
                        right_var.append(parse_args(temp))
                    print(is_func_call, func_name)

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

# bs for now
def parse_args(string):
    return [Variable(string[i] for i in string)]

class Func:
    def __init__(self, parent: Scope, text='', *args, **kwargs):
        self.name = '' 
        self.scope = Scope(parent, self.name)
        
        self.text = text
        self.nested = False
        self.lines: Dict[str, Line] = {}
        self._need_rebuild = True
        self.args: List[Variable] = []
        self.def_line = None
        self.nested_funcs = {}
        
        self.last_place = 0
        self.needs_inline = False
        self.function_calls = {}
        
        
        self.return_type = TYPE_ANY
        self.return_lines = []

    def build(self):
        self.get_return_lines()
        self.text = ''
        for i in range(self.last_place):
            if i in self.lines:
                for line in self.lines[i].sublines :
                    self.scope.add(*line.left_var)
        self.scope.wrap_childs()
        for i in range(self.last_place):
            if i in self.lines:
                self.lines[i].rebuild()
                self.text += self.lines[i].text + '\n'
            elif i in self.nested_funcs:
                self.text += str(self.nested_funcs[i]) + '\n'
            
        with open('build/{}.py'.format(self.name), 'w') as f:
            f.write(self.text)

    def __repr__(self):
        if self._need_rebuild:
            self.build()
        return self.text

    def set_rebuild(self):
        self._need_rebuild = True

    def get_return_lines(self):
        self.return_lines = []
        for _, line in self.lines.items():
            if line.is_return_line:
                self.return_lines.append(line)
        for line in self.return_lines:
            print(line.text)

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
        self.scope.name = self.name
        _, comment = remove_comment(self.def_line)
        if 'inline' in comment:
            self.needs_inline = True
        args = find_between(self.def_line.text, '(', ')')[0].split(',')
        self.args = []
        for arg in args:
            self.args.append(Variable(arg))

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


def process_with(text):
    return text


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
        return int(i / indent.length)
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


def get_func(lines: str, indent_char: str, i: int, parent_scope: Scope):
    local_func = Func(parent_scope)
    local_func.add_def_line(Line(lines[i]))
    local_func.parse_def_line()
    indent = indent_lvl(lines[i], indent_char)
    i += 1
    while indent_lvl(lines[i], indent_char) > indent and i < len(lines):
        if should_make_func(lines[i]):
            nested_func, i = get_func(
                lines[i:], indent_char, i-1, local_func.scope)
            local_func.add_nested_func(nested_func)
        else:
            local_func.append_line(Line(lines[i]))
        i += 1
    return local_func, i


def find_funcs(text: str):
    lines = text.split('\n')
    i = 0
    indent_char = get_indent_char(text)
    funcs = []
    while i < len(lines):
        if should_make_func(lines[i]):
            f, i = get_func(lines, indent_char, i, Scope(None, 'main'))
            f.build()
            funcs.append(f)
        i += 1
    return funcs


def process_for(string):
    return string


def parse_func():
    pass


def should_be_inlined():
    pass

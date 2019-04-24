import sys
import parser


with open(sys.argv[1], 'r') as f:
    content = f.read()
for f in parser.find_funcs(content):
    for j in f.nested_funcs:
        print(f.nested_funcs[j])
    print('args =', f.args)
    print('name = "{}"'.format(f.name))
    print(f)
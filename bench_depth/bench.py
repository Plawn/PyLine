import time
import sys

unit = 'us'


def str_to_bool(string: str):
    return 'true' == string.lower()


def gen_depth(depth, base_func):
    prec = base_func
    for _ in range(depth):
        prec = make_one(prec)
    return prec

def make_one(prec):
    return lambda a: prec(a)


def bench(func, times):
    t = time.time()
    for _ in range(times):
        func()
    return ((time.time() - t) / times) * 1_000_000  # to make => unit = us


def bench_depth(depth: int, func):
    return map(lambda f: (bench(lambda: f(10000), 100000)), [gen_depth(i, func) for i in range(depth)])


def is_slower(t1: float, t2: float):
    return abs((t1 - t2) / t2)


def dump_results(m: map, filename_csv, _print=True, filename_png=''):
    x, y,slower = [], [], []
    s = 'depth,call_time({})\n'.format(unit)
    t1 = 0
    for i, j in enumerate(m):
        if i == 0:
            t1 = j
        slowe = is_slower(t1, j)
        print(i, '=>', j, '%.2f' % (slowe*100) + '%', 'slower than depth 0')
        slower.append(100 - (slowe*100))
        x.append(i)
        y.append(j)
    s += '\n'.join(['{},{}'.format(i, j) for i, j in zip(x, y)])
    with open(filename_csv, 'w') as f:
        f.write(s)
    if _print:
        fig, ax1 = plt.subplots()
        ax1.plot(x, y)
        
        ax1.set_xlabel('Function call depth')
        ax1.set_ylabel('Time({})'.format(unit))
        ax2 = ax1.twinx()
        ax2.set_ylabel('relative speed',color='red')
        ax2.plot(x, slower, color='red')
        ax2.plot([0, len(y)], [50,50], color='purple')
        # plt.xlabel('Function call depth')
        # plt.ylabel('Time({})'.format(unit))
        if filename_png != '':
            plt.savefig(filename_png)
        plt.show()


max_depth = 20
_print = False
def base_func(a):
        a = 0
        for i in range (a):
            a += i
        return a


if len(sys.argv) > 1:
    max_depth = int(sys.argv[1])
    if len(sys.argv) > 2:
        _print = str_to_bool(sys.argv[2])
        import matplotlib.pyplot as plt


results = bench_depth(max_depth, base_func)
dump_results(results, 'results_{}.csv'.format(max_depth),
             _print, 'results_{}.png'.format(max_depth))

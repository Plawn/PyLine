from Minliner import inline


@inline
def u(e): #inline
    a = e * 2
    return a

def a_dje(b:int):
    p = []
    for i in range(b):
        p.append(i*2)
            



def dem(b:int):
    p = []
    for i in range(b):
        p.append(pp(i))

def pp(e):
    a = e * 2
    return a



import time
def bench(closure, times:int):
    t = time.time()
    for _ in range(times):
        closure()
    return (time.time() - t) / times


print(bench(lambda : a_dje(10000),1000))
print(bench(lambda : dem(10000),1000))
def bench(closure, times:int):
    bench_t=time.time()
    bench_p=0
    bench_l=1
    bench_o=0
    for _ in range(times):
        closure()
    _ =  (time.time() - t) / times
    return _


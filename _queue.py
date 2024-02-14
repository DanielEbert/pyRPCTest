import multiprocessing as mp
import time


def source(q):
    for i in range(100_000):
        q.put(i)


def sink(q):
    start_time = time.time()
    recv_count = 0
    while True:
        q.get(block=True)
        recv_count += 1
        if recv_count == 100_000:
            print('done')
            print(round(time.time() - start_time, 2))


source_q = mp.Queue()
sink_q = mp.Queue()

source_proc = mp.Process(target=source, args=(source_q, ))
source_proc.start()
sink_proc = mp.Process(target=sink, args=(sink_q, ))
sink_proc.start()

while True:
    ret = source_q.get(block=True)
    sink_q.put(ret)

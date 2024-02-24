from __future__ import annotations

import multiprocessing as mp
import ormsgpack
import time


start_time = time.time()

def sink(q):
    recv_count = 0
    while True:
        if not q.poll():
            continue

        elem = q.recv()
        recv_count += len(elem)
        if recv_count % 100 == 0:
            print(recv_count, 'MB/s:', round(recv_count / (time.time() - start_time) / 1000000, 2))

def source(q):
    inc_list = [i for i in range(1000)]
    i = 0
    while True:
        q.send(ormsgpack.packb({
            'x': (i + 1) % 5,
            'y': i % 5,
            'z': f'some{i}long{i+1}string{i+2}',
            'l': inc_list
        }))

recv_source_q, send_source_q = mp.Pipe()
recv_sink_q, send_sink_q = mp.Pipe()

# source_proc = mp.Process(target=source, args=(send_source_q, ))
# source_proc.start()
sink_proc = mp.Process(target=sink, args=(recv_sink_q, ))
sink_proc.start()

source(send_sink_q)

# while True:
#     ret = recv_source_q.recv()
#     send_sink_q.send(ret)

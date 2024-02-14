from __future__ import annotations

import multiprocessing as mp
import time
import ormsgpack

import socketio
import eventlet
import json
import random

import asyncio
import websockets
from websockets.server import serve

spec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.15.1.json",
    "config": {
        "view":
            {"continuousHeight":500,"continuousWidth":500}
        },
        "layer": [
            {
                "data":{"name":"source"},
                "encoding": {
                    "x":{"field":"x","type":"quantitative"},
                    "y":{"field":"y","type":"quantitative"},
                    "tooltip": {"field":"z","type":"nominal"}
                },
                "mark":{"type":"point"},
                "name":"view_15",
            },
            {
                "data":{"name":"sourceb"},
                "encoding":{
                    "x":{"field":"a","type":"quantitative"},
                    "y":{"field":"b","type":"quantitative","scale":{"domain":[0,{"expr":"domainWidth"}]}}
                },
                "mark":{"color":"red","type":"point"},
                "name":"view_16"
            }
        ],
        "params":[
            {
                "name":"domainWidth",
                "value":10,
                "bind":{"input":"range","min":1,"max":20,"step":1,"name":"Domain Width "}
            },
            {
                "name":"filterStart","value": 0
            }
        ]
    }


def sink(q):
    connections = set()

    # TODO: similar to socketio, send spec etc on register
    async def register(ws):
        connections.add(ws)
        print('registed', ws)
        try:
            await ws.wait_closed()
        finally:
            connections.remove(ws)
    
    async def send():
        recv_count = 0
        while True:
            if not q.poll() or not connections:
                await asyncio.sleep(0.01)
                continue

            elem = q.recv()
            recv_count += 1
            if recv_count == 100_000:
                print('done sending')

            websockets.broadcast(connections, elem)

    async def main():
        async with serve(register, "localhost", 8765):
            await send()

    asyncio.run(main())

"""
def sink(q) -> int:
    sio = socketio.Server(cors_allowed_origins='*')

    client_ids = {}

    @sio.event
    def connect(sid, environ, auth):
        print('connect ', sid)
        client_ids[sid] = {'next_t': 0}

    @sio.event
    def disconnect(sid):
        print('disconnect ', sid)
        del client_ids[sid]

    @sio.event
    def register_for_plot(sid, data):
        print('register_for_plot', sid, data)
        return json.dumps(
            {
                'spec': spec,
                # 'initial_data': [
                #     { 'x': 1, 'y': 3, 't': 0 },
                #     { 'x': 2, 'y': 2, 't': 0 },
                #     { 'x': 3, 'y': 1, 't': 0 },
                #     { 'x': 4, 'y': 4, 't': 0 },
                #     { 'x': 5, 'y': 5, 't': 0 },
                # ],
            }
        )

    def send_new_data():
        recv_count = 0
        eventlet.sleep(1)
        while True:
            if not q.poll():
                eventlet.sleep(0.01)
                continue

            elem = q.recv()
            recv_count += 1
            if recv_count == 100_000:
                print('done sending')

            for sid, sid_data in client_ids.items():
                sio.emit('newData', elem, room=sid)

    app = socketio.WSGIApp(sio)
    eventlet.spawn(send_new_data)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
"""

def source(q):
    inc_list = [i for i in range(1000)]
    for i in range(100_000):
        q.send(ormsgpack.packb({
            'x': (i + 1) % 5,
            'y': i % 5,
            'z': f'some{i}long{i+1}string{i+2}',
            'l': inc_list
        }))


send_source_q, recv_source_q = mp.Pipe()
send_sink_q, recv_sink_q = mp.Pipe()

source_proc = mp.Process(target=source, args=(send_source_q, ))
source_proc.start()
sink_proc = mp.Process(target=sink, args=(recv_sink_q, ))
sink_proc.start()

while True:
    ret = recv_source_q.recv()
    send_sink_q.send(ret)

from websockets.sync.client import connect

def hello():
    recv_count = 0
    with connect("ws://localhost:8765") as websocket:
        while True:
            if recv_count == 0:
                print(websocket.recv())
            recv_count += 1
            if recv_count % 1000 == 1:
                print(recv_count)
            message = websocket.recv()

hello()

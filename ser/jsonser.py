import json

inc_list = [i for i in range(1000)]

for i in range(100_000):
    json.dumps(
        {
            'x': i,
            'y': i * 1.2,
            'z': f'some{i}long{i+1}string{i+2}',
            'l': inc_list
        }
    )
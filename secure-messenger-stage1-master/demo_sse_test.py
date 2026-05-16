import requests
import json
import threading
import time

print('demo start')

s = requests.post('http://127.0.0.1:8000/login', json={'username': 'bob', 'password': 'bob456'})
print('bob login', s.status_code, s.text)
token = s.json()['access_token']
h = {'Authorization': f'Bearer {token}'}


def listen():
    r = requests.get('http://127.0.0.1:8000/stream', headers=h, stream=True, timeout=None)
    print('stream status', r.status_code)
    for line in r.iter_lines():
        if not line:
            continue
        line_str = line.decode()
        if line_str.startswith('data: '):
            print('GOT:', json.loads(line_str[6:]))
            break

threading.Thread(target=listen, daemon=True).start()
time.sleep(1)

a = requests.post('http://127.0.0.1:8000/login', json={'username': 'alice', 'password': 'alice123'})
print('alice login', a.status_code, a.text)
at = a.json()['access_token']
r = requests.post(
    'http://127.0.0.1:8000/messages',
    headers={'Authorization': f'Bearer {at}'},
    json={'recipient': 'bob', 'content': 'hello from alice'},
)
print('send status', r.status_code, r.text)
time.sleep(5)

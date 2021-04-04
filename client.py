import sseclient

messages = sseclient.SSEClient('http://localhost:8000/event')

for msg in messages:
  print(msg)
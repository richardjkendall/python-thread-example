import threading
from flask import Flask, request, Response, make_response

def synchronized_with_attr(lock_name):
    
  def decorator(method):
			
    def synced_method(self, *args, **kws):
      lock = getattr(self, lock_name)
      with lock:
        return method(self, *args, **kws)
                
    return synced_method
    
  return decorator

def success_json_response(payload):
  """
  Turns payload into a JSON HTTP200 response
  """
  response = make_response(jsonify(payload), 200)
  response.headers["Content-type"] = "application/json"
  return response

def format_sse(data: str, event=None) -> str:
  msg = f'data: {data}\n\n'
  if event is not None:
    msg = f'event: {event}\n{msg}'
  return msg
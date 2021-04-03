import logging
import atexit
import json
from flask import Flask, request, Response, make_response
from flask_cors import CORS
from backend import get_backend
from utils import format_sse, success_json_response

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger(__name__)

bthread = get_backend()

@app.route("/", methods=["GET"])
def root():
  """
  Root function
  """
  return success_json_response({
    "status": "okay"
  })

@app.route("/send", methods=["POST"])
def send():
  if request.json:
    if "message" in request.json:
      bthread.send(request.json["message"])
    else:
      return success_json_response({
        "error": "no message field"
      })
  else:
    return success_json_response({
      "error": "not a JSON request"
    })

@app.route("/event", methods=["GET"])
def listen():
  def stream():
    q = bthread.listen()
    while True:
      message = q.get()
      yield format_sse(message, "message")
  return Response(stream(), mimetype="text/event-stream")
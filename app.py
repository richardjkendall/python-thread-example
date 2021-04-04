import logging
import atexit
import json
from flask import Flask, request, Response, make_response
from flask_cors import CORS
from backend import Backend
from utils import format_sse, success_json_response

app = Flask(__name__)
CORS(app)

logger = logging.getLogger(__name__)

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
  logger.info("In send method...")
  bend = Backend.create_instance()
  if request.json:
    logger.info("Request is JSON")
    if "message" in request.json:
      logger.info("Calling send method...")
      bend.send(request.json["message"])
      return success_json_response({
        "status": "okay",
        "notes": "message sent"
      })
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
  logger.info("In event method...")
  bend = Backend.create_instance()
  def stream():
    q = bend.listen()
    logger.info("Got queue to listen to...")
    while True:
      logging.info("Waiting for message")
      message = q.get()
      logging.info("Got a message...")
      yield format_sse(message, "message")
  return Response(stream(), mimetype="text/event-stream")
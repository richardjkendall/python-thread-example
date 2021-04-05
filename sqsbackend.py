import logging
import boto3

from gevent.queue import Queue
from gevent.event import Event
from gevent.lock import BoundedSemaphore

from decouple import config

sqs = boto3.client("sqs")
logger = logging.getLogger(__name__)
sqs_backend = None
lock = BoundedSemaphore(1)

class SqsBackend():

  def __init__(self, queueurl):
    self.out_queues = []
    self.queueurl = queueurl
    self.stoprequest = Event()

  def listen(self):
    logger.info("Listening...")
    q = Queue(maxsize=5)
    self.out_queues.append(q)
    return q

  def stop(self):
    logger.info("Setting stop event")
    self.stoprequest.set()

  def run(self):
    while not self.stoprequest.isSet():
      logger.info("Starting long poll of sqs queue...")
      response = sqs.receive_message(
        QueueUrl=self.queueurl,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
      )
      logger.info("Back from long poll")
      if "Messages" in response:
        for message in response["Messages"]:
          body = message["Body"]
          recphwnd = message["ReceiptHandle"]
          logger.info(body)
          for i in reversed(range(len(self.out_queues))):
            try:
              logger.info("Putting message on queue")
              self.out_queues[i].put_nowait(message)
            except:
              logger.info("Removing full queue")
              del self.out_queues[i]
          sqs.delete_message(
            QueueUrl=self.queueurl,
            ReceiptHandle=recphwnd
          )
      else:
        logger.info("Got no messages during long poll")
  
  def join(self, timeout=None):
    logger.info("Joining...")
    self.stoprequest.set()

def get_backend():
  global sqs_backend
  with lock:
    if sqs_backend:
      logger.info("Returning existing backend instance")
      return sqs_backend
    else:
      logger.info("Creating new backend instance")
      sqs_backend = SqsBackend(
        queueurl=config("queue")
      )
      return sqs_backend
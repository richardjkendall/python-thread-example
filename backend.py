import threading
import queue
import logging
from utils import synchronized_with_attr

bthread = None
logger = logging.getLogger(__name__)

class Backend(object):

  instance = None
  lock = threading.Lock()

  def __init__(self):
    self.out_queues = []
    self.stoprequest = threading.Event()
  
  @staticmethod
  def create_instance():
    logger.info("In create_instance")
    with Backend.lock:
      if not Backend.instance:
        logger.info("Instance is not initialised, so creating")
        Backend.instance = Backend()
      return Backend.instance

  def listen(self):
    logger.info("Listening...")
    q = queue.Queue(maxsize=5)
    self.out_queues.append(q)
    return q

  def send(self, message):
    logger.info("In send method")
    for i in reversed(range(len(self.out_queues))):
      try:
        logger.info("Putting message on queue")
        self.out_queues[i].put_nowait(message)
      except:
        del self.out_queues[i]
    logger.info("Send method complete")
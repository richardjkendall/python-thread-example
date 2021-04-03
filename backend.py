import threading
import queue
import logging
from utils import synchronised

bthread = None

logger = logging.getLogger(__name__)

@synchronised
def get_backend():
  global bthread
  print(bthread)
  if not bthread:
    logger.info("Getting instance of backend...")
    bthead = BackendThread(tname="backend")
  logger.info("Returning backend")
  return bthead

class BackendThread(threading.Thread):

  def __init__(self, tname):
    super(BackendThread, self).__init__(name=tname)
    self.tname = tname
    self.in_queue = queue.Queue()
    self.out_queues = []
    self.stoprequest = threading.Event()
  
  def listen(self):
    q = queue.Queue(maxsize=5)
    self.out_queues.append(5)
    return q

  def send(self, message):
    self.in_queue.put_nowait(message)

  def run(self):
    while not self.stoprequest.isSet():
      try:
        msg = self.in_queue.get(True, 0.05)
        for i in reversed(range(len(self.out_queues))):
          try:
            self.out_queues[i].put_nowait(msg)
          except:
            del self.out_queues[i]
      except queue.Empty:
        continue
  
  def join(self, timeout=None):
    self.stoprequest.set()
    super(BackendThread, self).join(timeout)

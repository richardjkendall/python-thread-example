from gevent import monkey
monkey.patch_all()

import logging
from gunicorn.app.base import Application, Config
from app import app
from sqsbackend import get_backend
from gevent import Greenlet

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger(__name__)

SqsThread = None

class GUnicornFlaskApplication(Application):
  def __init__(self, app):
    self.usage, self.callable, self.prog, self.app = None, None, None, app
    
  def run(self, **options):
    self.cfg = Config()
    [self.cfg.set(key, value) for key, value in options.items()]
    return Application.run(self)

  load = lambda self:self.app

def starting(worker):
  logger.info("on_starting called")
  global sqs_g 
  sqs_g = Greenlet(get_backend().run)
  sqs_g.start()

def stopping(server, worker):
  logger.info("on_exit called")
  global sqs_g
  sqs_g.join(timeout=2)

if __name__ == "__main__":
  g_app = GUnicornFlaskApplication(app)
  g_app.run(
    worker_class="gevent",
    workers=1,
    post_worker_init=starting,
    worker_exit=stopping
  )
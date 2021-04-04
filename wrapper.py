import logging
from gunicorn.app.base import Application, Config
from app import app
from backend import Backend


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s")
logger = logging.getLogger(__name__)

bend = None

class GUnicornFlaskApplication(Application):
    
  def __init__(self, app):
    self.usage, self.callable, self.prog, self.app = None, None, None, app
    
  def run(self, **options):
    self.cfg = Config()
    [self.cfg.set(key, value) for key, value in options.items()]
    return Application.run(self)

  load = lambda self:self.app

if __name__ == "__main__":
  bend = Backend.create_instance()
  g_app = GUnicornFlaskApplication(app)
  g_app.run(
    worker_class="gevent"
  )
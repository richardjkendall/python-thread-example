import pika
import threading
import logging
from backend import Backend

logger = logging.getLogger(__name__)

class MQThread(threading.Thread):
  def __init__(self):
    super(MQThread, self).__init__()

  def _callback(self, ch, method, properties, body):
    logger.info("Got a message from MQ")
    logger.info(f"Message from MQ is {body}")
    bend = Backend.create_instance()
    logger.info(f"Backend instance {bend}")
    bend.send(body.decode("utf-8"))

  def run(self):
    logger.info("Starting, creating the MQ objects...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    self.channel = connection.channel()
    self.channel.queue_declare(queue="messages")
    self.channel.basic_consume(queue="messages", on_message_callback=self._callback, auto_ack=True)
    logger.info("Starting consumer...")
    self.channel.start_consuming()

  def join(self, timeout):
    logger.info("Joining MQ thread")
    self.channel.stop_consuming()
    logger.info("Sent basic cancel...")
    super(MQThread, self).join(timeout)
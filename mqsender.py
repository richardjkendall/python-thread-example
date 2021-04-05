import pika
import json

message = {
  "body": "hello",
  "message_id": "123"
}

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue="messages")
channel.basic_publish(exchange='test', routing_key="messages", body=json.dumps(message))
connection.close()
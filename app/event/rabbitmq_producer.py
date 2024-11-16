import pika
import json

def produce_message(user_data, field):
    try:
        # Establish connection to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue='user_updates')

        message = {
            "user_id": str(user_data["_id"]),
            field: user_data[field]
        }

        print(f"Message: {message}")

        # Send the user data to RabbitMQ
        channel.basic_publish(exchange='', routing_key='user_updates', body=json.dumps(message))
        print(" [x] Sent user data to queue")

        # Close the connection
        connection.close()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")
    except pika.exceptions.ChannelError as e:
        print(f"Failed to open a channel: {e}")
    except Exception as e:
        print(f"Failed to produce message: {e}")
import pika
import json
import logging
from fastapi import HTTPException
from mongodb import mongo_client
from bson import ObjectId

order_db = mongo_client.order
orders_coll = order_db.orders

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

def consume_message():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue='user_updates')

        method_frame, header_frame, body = channel.basic_get(queue='user_updates', auto_ack=True)

        if body:
            event_data = json.loads(body)
            user_id = event_data.get('user_id')

            field, new_field_value = retrieve_modified_field(event_data)

            if user_id is not None and new_field_value is not None:
                if update_orders_field_with_user_id(user_id, field, new_field_value):
                    logging.info(f"Updated {field} for user {user_id} in orders collection")
                else:
                    logging.warning(f"Failed to update {field} for user {user_id} in orders collection")
            else:
                logging.warning("Invalid message received")
        else:
            logging.info("No messages in the queue to consume.")

        connection.close()

    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Connection to RabbitMQ failed: {e}")

def retrieve_modified_field(event_data):
    field = None
    new_field_value = None

    if 'email' in event_data:
        field = 'user_email'
        new_field_value = event_data['email']
    elif 'delivery_address' in event_data:
        field = 'delivery_address'
        new_field_value = event_data['delivery_address']

    return field, new_field_value

def update_orders_field_with_user_id(user_id, field, value):
    try:
        user_id_obj = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order_id format")

    result = orders_coll.update_many({"user_id": user_id_obj}, {"$set": {field: value}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found while consuming message")

    updated_orders = list(orders_coll.find({"user_id": user_id_obj}))
    return updated_orders
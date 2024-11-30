import pika
import json
import logging
from fastapi import HTTPException, FastAPI
from mongodb import mongo_client
from data_models.models import ProducerMessageRequest
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

rabbitmq = os.getenv("RABBITMQ_URL")
param = pika.URLParameters(rabbitmq)
order_db = mongo_client.order
orders_coll = order_db.orders

app = FastAPI()

@app.post("/message")
def produce_message(request: ProducerMessageRequest):
    try:
        # Establish connection to RabbitMQ
        connection = pika.BlockingConnection(param)
        channel = connection.channel()
        channel.queue_declare(queue='user_updates')

        message = {
            "user_id": str(request.user_data["_id"]),
            request.field: request.user_data[request.field]
        }

        channel.basic_publish(exchange='', routing_key='user_updates', body=json.dumps(message))
        logging.info(f"[x] Sent message: {message}")

        connection.close()
        return {"status": "success", "message": "Message sent to RabbitMQ"}
    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"RabbitMQ connection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ")
    except Exception as e:
        logging.error(f"Failed to produce message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/message")
def consume_message():
    try:
        connection = pika.BlockingConnection(param)
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
                    return {"status": "success", "message": "Orders updated successfully"}
                else:
                    raise HTTPException(status_code=404, detail="Orders not found for the user")
            else:
                raise HTTPException(status_code=400, detail="Invalid message format")
        else:
            return {"status": "success", "message": "No messages to consume"}

    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Connection to RabbitMQ failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ")
    finally:
        if connection.is_open:
            connection.close()
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
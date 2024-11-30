import os
from typing import Union

from bson import ObjectId
from fastapi import FastAPI, HTTPException
import requests
from data_models.models import User, DeliveryAddress, UsersUpdateDeliveryAddressRequest, UsersUpdateEmailRequest
from mongodb import mongo_client

events_service = os.getenv("EVENTS_SERVICE")
event_produce_url = f"{events_service}/message"
# event_produce_url = "http://events-service:8083/message"
app = FastAPI()

@app.get("/api/v1/read-all-users")
def get_users():
    user_db = mongo_client.user
    users_coll = user_db.users
    cursor = users_coll.find({})
    users = []
    for record in cursor:
        record['_id'] = str(record['_id'])
        users.append(record)
    return {"users": users}

@app.post("/api/v1/create-user", response_model=User)
def insert_user(user: User):
    user_db = mongo_client.user
    users_coll = user_db.users
    result = users_coll.insert_one(user.model_dump())
    inserted_user = users_coll.find_one({"_id": result.inserted_id})
    return inserted_user

def update_users_field(user_id, field, value):
    user_db = mongo_client.user
    users_coll = user_db.users

    try:
        user_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    result = users_coll.update_one({"_id": user_id}, {"$set": {field: value}})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = users_coll.find_one({"_id": user_id})
    if updated_user:
        updated_user["_id"] = str(updated_user["_id"])
        requests.post(event_produce_url, json={
            "user_data": updated_user,
            "field": field})
        # produce_message(updated_user, field)
        return updated_user
    else:
        raise HTTPException(status_code=404, detail="User not found after update")

@app.put("/api/v1/update-user-field", response_model=User)
def update_user_field(request: Union[UsersUpdateDeliveryAddressRequest, UsersUpdateEmailRequest]):
    if isinstance(request, UsersUpdateDeliveryAddressRequest):
        return update_users_field(request.user_id, "delivery_address", request.delivery_address.dict())
    elif isinstance(request, UsersUpdateEmailRequest):
        return update_users_field(request.user_id, "email", request.email)
    else:
        raise HTTPException(status_code=400, detail="Invalid request type")
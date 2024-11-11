from bson import ObjectId
from fastapi import FastAPI, HTTPException
from data_models.models import User, DeliveryAddress, UsersUpdateDeliveryAddressRequest, UsersUpdateEmailRequest
from mongodb import mongo_client
from pydantic import BaseModel

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
        return updated_user
    else:
        raise HTTPException(status_code=404, detail="User not found after update")

@app.put("/api/v1/update-delivery-address", response_model=User)
def update_delivery_address(request: UsersUpdateDeliveryAddressRequest):
    return update_users_field(request.user_id, "delivery_address", request.delivery_address.dict())

@app.put("/api/v1/update-email", response_model=User)
def update_email_address(request: UsersUpdateEmailRequest):
    return update_users_field(request.user_id, "email", request.email)
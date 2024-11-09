from fastapi import FastAPI
from data_models.models import User
from mongodb import mongo_client

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
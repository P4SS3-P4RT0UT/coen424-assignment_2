import random

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from dotenv import load_dotenv
import os
load_dotenv()

""" 
API Gateway code adapted from from Punnyartha Banerjee on Medium: 
https://medium.com/@punnyarthabanerjee/build-a-gateway-for-microservices-in-fastapi-73e44fe3573b
"""

app = FastAPI()

users_service = os.getenv("USERS_SERVICE")
users_v2_service = os.getenv("USERS_V2_SERVICE")
orders_service = os.getenv("ORDERS_SERVICE")
routing_percentage = int(os.getenv("ROUTING_PERCENTAGE"))

services = {
    "users": {
        "v1": f"{users_service}api/v1",
        "v2": f"{users_v2_service}api/v2"
    },
    "orders": f"{orders_service}api/v1"
}

# for local
# services = {
#     "users": {
#         "v1": "http://127.0.0.1:8082/api/v1",
#         "v2": "http://127.0.0.1:8084/api/v2"
#     },
#     "orders": "http://127.0.0.1:8080/api/v1"
# }

def user_routing(service, service_list):
    if service == "users":
        if random.randint(1, 100) < routing_percentage:
            service_url = service_list[service]["v1"]
        else:
            service_url = service_list[service]["v2"]
    else:
        service_url = service_list[service]
    return service_url


async def forward_request(service_url: str, method: str, path: str, body=None, headers=None):
    url = f"{service_url}/{path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=body, headers=headers)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.ConnectError as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(service: str, path: str, request: Request):
    if service not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    service_url = user_routing(service, services)
    body = await request.json() if request.method in ["POST", "PUT"] else None
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = await forward_request(service_url, request.method, path, body, headers)

    return JSONResponse(status_code=response.status_code, content=response.json())

if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from dotenv import load_dotenv
import os
load_dotenv()

""" 
API Gateway code taken from https://medium.com/@punnyarthabanerjee/build-a-gateway-for-microservices-in-fastapi-73e44fe3573b
"""

app = FastAPI()

users_service = os.getenv("USERS_SERVICE")
orders_service = os.getenv("ORDERS_SERVICE")

services = {
    "users": f"{users_service}api/v1",
    "orders": f"{orders_service}api/v1"
}

async def forward_request(service_url: str, method: str, path: str, body=None, headers=None):
    url = f"{service_url}/{path}"
    print(f"Forwarding request to: {url}")

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
    print(f"service: {service} and path: {path}")
    if service not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    service_url = services[service]
    body = await request.json() if request.method in ["POST", "PUT"] else None
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = await forward_request(service_url, request.method, path, body, headers)

    return JSONResponse(status_code=response.status_code, content=response.json())

if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')

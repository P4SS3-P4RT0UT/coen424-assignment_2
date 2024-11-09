from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import uvicorn

""" 
API Gateway code taken from https://medium.com/@punnyarthabanerjee/build-a-gateway-for-microservices-in-fastapi-73e44fe3573b
"""

app = FastAPI()

services = {
    "users": "http://127.0.0.1:8080",
    "orders": "http://127.0.0.1:8080"
}

async def forward_request(service_url: str, method: str, path: str, body=None, headers=None):
    async with httpx.AsyncClient() as client:
        url = f"{service_url}{path}"
        print(f"Forwarding request to: {url}")
        response = await client.request(method, url, json=body, headers=headers)
        return response

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(service: str, path: str, request: Request):
    print(f"service: {service} and path: {path}")
    if service not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    service_url = services[service]
    body = await request.json() if request.method in ["POST", "PUT"] else None
    headers = dict(request.headers)

    response = await forward_request(service_url, request.method, f"/{path}", body, headers)

    return JSONResponse(status_code=response.status_code, content=response.json())

if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')
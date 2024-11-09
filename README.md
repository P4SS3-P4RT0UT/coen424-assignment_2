# PROJECT SETUP
1. Create virtual environment
2. Activate virtual environment
3. Run `pip install -r requirements.txt`
4. Add .env file to assignment files

# REST APIS 
In order to run the app and evaluate the APIs (locally), run the following command:
`uvicorn app:app --reload`
<br />
<br />
Query examples: 
- POST (/api/v1/create-user): `curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/create-user' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "frank.taylor@protonmail.com",
  "first_name": "Frank",
  "last_name": "Taylor",
  "date_of_birth": "1972-06-18",
  "phone_number": "1234567890",
  "delivery_address": {
    "street": "234 Cedar Ln",
    "city": "Houston",
    "state": "TX",
    "zip_code": "77002",
    "country": "USA"
  }
}'`
- POST (/api/v1/create-order): curl -X 'POST' \
  'http://localhost:8000/api/v1/create-order/' \
  -H 'Content-Type: application/json' \
  -d '{
    "user_email": "george.smith@protonmail.com",
    "delivery_address": {
      "street": "123 Elm St",
      "city": "Metropolis",
      "state": "NY",
      "zip_code": "12345",
      "country": "USA"
    },
    "items": [
      {
        "item_id": "ITM003",
        "name": "Screwdriver Set",
        "quantity": 1,
        "price": 15.49
      },
      {
        "item_id": "ITM004",
        "name": "Adjustable Wrench",
        "quantity": 1,
        "price": 8.99
      }
    ],
    "order_status": "shipping",
    "total_amount": 24.48
  }'



http://localhost:8000/read_users/api/v1/read-all-users
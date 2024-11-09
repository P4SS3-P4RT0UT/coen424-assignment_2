# PROJECT SETUP
1. Create virtual environment
2. Activate virtual environment
3. Run `pip install -r requirements.txt`
4. Add .env file to assignment files

# REST APIS 
In order to run the app and evaluate the APIS, run the following command:
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




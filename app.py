from flask import Flask, request, jsonify
import requests
import base64
from datetime import datetime

app = Flask(__name__)

# MPesa Sandbox credentials
BUSINESS_SHORTCODE = "174379"  # Sandbox Shortcode
LIPA_NA_MPESA_PASSKEY = "bfb279f4f9b3a265f0c2f0e217dbd72e"  # Sandbox Passkey
CONSUMER_KEY = "YourConsumerKeyHere"
CONSUMER_SECRET = "YourConsumerSecretHere"

# MPesa Base URLs
SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"

def get_access_token():
    """
    Get an OAuth access token from MPesa API.
    """
    url = f"{SANDBOX_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    access_token = response.json().get("access_token")
    return access_token

def generate_password():
    """
    Generate the Base64-encoded password required for STK Push.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = BUSINESS_SHORTCODE + LIPA_NA_MPESA_PASSKEY + timestamp
    encoded_password = base64.b64encode(data_to_encode.encode()).decode()
    return encoded_password, timestamp

@app.route('/mpesa-push', methods=['POST'])
def lipa_na_mpesa():
    """
    Handle STK Push requests from the frontend.
    """
    # Get data from the frontend
    data = request.json
    phone_number = data.get("phone")
    amount = data.get("amount")

    # Generate access token
    access_token = get_access_token()

    # Generate password and timestamp
    password, timestamp = generate_password()

    # STK Push request payload
    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,  # Customer's phone number
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://your-callback-url.com/callback",  # Replace with your callback URL
        "AccountReference": "TestPayment",
        "TransactionDesc": "Payment for Test"
    }

    # Make STK Push request
    url = f"{SANDBOX_BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, json=payload, headers=headers)

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)


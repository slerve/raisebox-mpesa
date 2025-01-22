from flask import Flask, request, jsonify
import requests
from datetime import datetime
import base64

app = Flask(__name__)

# Replace these with your credentials
BUSINESS_SHORTCODE = "123456"
LIPA_NA_MPESA_PASSKEY = "YourPassKeyHere"
CONSUMER_KEY = "YourConsumerKeyHere"
CONSUMER_SECRET = "YourConsumerSecretHere"

# Safaricom API URLs
MPESA_AUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
MPESA_STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"


def get_access_token():
    response = requests.get(MPESA_AUTH_URL, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    response_data = response.json()
    return response_data.get("access_token")


def initiate_stk_push(phone, amount):
    access_token = get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (BUSINESS_SHORTCODE + LIPA_NA_MPESA_PASSKEY + timestamp).encode("utf-8")
    ).decode("utf-8")

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": "https://your-callback-url.com/callback",
        "AccountReference": "MPesaPayment",
        "TransactionDesc": "Payment for goods or services"
    }

    response = requests.post(MPESA_STK_PUSH_URL, json=payload, headers=headers)
    return response.json()


@app.route("/mpesa-push", methods=["POST"])
def mpesa_push():
    data = request.json
    phone = data.get("phone")
    amount = data.get("amount")

    if not phone or not amount:
        return jsonify({"message": "Phone and amount are required"}), 400

    response = initiate_stk_push(phone, amount)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)

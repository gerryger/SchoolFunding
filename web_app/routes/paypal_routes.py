import os, requests, aiohttp
from flask import Blueprint, jsonify, request, render_template, current_app , session
from flask_wtf import CSRFProtect
from base64 import b64encode

from web_app.routes.wrappers import authenticated_route

paypal_routes = Blueprint("paypal_routes", __name__)

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID");
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET");
BASE_URL = os.getenv("PAYPAL_URL")

# Configure CSRF protection
csrf = CSRFProtect(current_app)

# Generate an OAuth 2.0 access token for authenticating with PayPal REST APIs.
# @see https://developer.paypal.com/api/rest/authentication/
def generate_access_token():
    try:
        if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
            raise Exception("MISSING_API_CREDENTIALS")
        
        auth = f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}"
        auth_base64 = b64encode(auth.encode()).decode('ascii')
        headers = {
            "Authorization": f"Basic {auth_base64}"
        }
        payload = {
            "grant_type": "client_credentials"
        }

        response = requests.post(f"{BASE_URL}/v1/oauth2/token", data=payload, headers=headers)
        data = response.json()

        return jsonify({'access_token': data.get('access_token')})
    except Exception as error:
        print("Failed to generate Access Token:", error)
        return jsonify({'error': str(error)}), 500
    
async def handle_response(response):
    try:
        jsonResponse = await response.json()
        return {
            'jsonResponse': jsonResponse,
            'httpStatusCode': response.status,
        }
    except Exception as err:
        errorMessage = await response.text()
        raise ValueError(errorMessage)
    
#
# Create an order to start the transaction.
# @see https://developer.paypal.com/docs/api/orders/v2/#orders_create
#
def handle_create_order():
    try:
        cart = request.json  # Assuming the cart information is sent as JSON in the request
        print("Shopping cart information passed from the frontend create_order() callback:", cart)

        access_token = generate_access_token()
        url = f"{BASE_URL}/v2/checkout/orders"
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": cart['fundhub_cart_id'],
                    "amount": {
                        "currency_code": "USD",
                        "value": cart['price'],
                    },
                },
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.post(url, json=payload, headers=headers)
        result = handle_response(response)

        return jsonify(result)

    except Exception as error:
        return jsonify({'error': str(error)}), 500
    
def create_cart(cart):
    service = current_app.config["FIREBASE_SERVICE"]
    user = service.find_user_by_email(cart["user_email"])
    
@paypal_routes.route('/paypal/orders', methods=['POST'])
def create_order():
    try:
        request_data = request.get_json()
        cart = request_data.get('cart', {})
        print("Shopping cart information passed from the frontend create_order() callback:", cart)

        create_cart({
            "user_email": session["current_user"]["email"],
            
        })

        # Assuming createOrder is a function similar to the one you provided earlier
        result = handle_create_order(cart)

        return jsonify(result)

    except Exception as error:
        print("Failed to create order:", error)
        return jsonify({'error': 'Failed to create order.'}), 500
import requests
import datetime
import logging
from google.cloud import secretmanager
from google.cloud import storage
import os
import json

# Initialize the Cloud Storage client
storage_client = storage.Client()
bucket_name = os.getenv('GCS_BUCKET_NAME')
bucket = storage_client.bucket(bucket_name)

# Load previously alert data from Google Cloud Storage

def load_alerted_orders():
    print("Loading alerted orders from Google Cloud Storage...")
    try:
        blob = bucket.blob("alerts.json")
        if blob.exists():
            data = blob.download_as_string()
            return json.loads(data)
        else:
            return []
    except Exception as e:
        print(f"Error loading alerted orders: {e}")
        return []

# Save alert data to Google Cloud Storage
def save_alerted_orders(alerted_orders):
    print("Saving alerted orders to Google Cloud Storage...")
    try:
        blob = bucket.blob("alerts.json")
        blob.upload_from_string(json.dumps(alerted_orders))
        print("Alerted orders saved successfully.")
    except Exception as e:
        print(f"Error saving alerted orders: {e}")

def access_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv('GCP_PROJECT') or os.getenv('GOOGLE_CLOUD_PROJECT')
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

SHOPIFY_ACCESS_TOKEN = access_secret("SHOPIFY_ACCESS_TOKEN")
print("Accessed SHOPIFY_ACCESS_TOKEN from Secret Manager.")
SHOPIFY_STORE_NAME = access_secret("SHOPIFY_STORE_NAME")
print("Accessed SHOPIFY_STORE_NAME from Secret Manager.")

def check_unfulfilled_orders():
    print("Checking for unfulfilled orders...")
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }
    url = f'https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/orders.json'
    params = {
        "status": "open",
        "fulfillment_status": "unfulfilled",
        "created_at_max": (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()
    }
    print("Sending request to Shopify API...")
    response = requests.get(url, headers=headers, params=params)
    print(f"Received response: {response.status_code}")
    orders = response.json().get("orders", [])

    alerted_orders = load_alerted_orders()
    new_alerted_orders = []

    unfulfilled_orders = [
        order for order in orders if not order.get('fulfillment_status') and order['order_number'] not in alerted_orders
    ]

    if unfulfilled_orders:
        print(f"Found {len(unfulfilled_orders)} unfulfilled orders that need notification.")
        send_notification(unfulfilled_orders)
        new_alerted_orders = [order['order_number'] for order in unfulfilled_orders]

    # Update the list of alerted orders
    alerted_orders.extend(new_alerted_orders)
    save_alerted_orders(alerted_orders)

def send_notification(orders):
    print("Sending notifications for unfulfilled orders...")
    for order in orders:
        message = f"Order {order['order_number']} has been unfulfilled for over 10 days."
        print(f"Notification: {message}")
        # Optionally, integrate with an email or SMS service here

def main(request):
    print("Starting main function...")
    check_unfulfilled_orders()
    return "Check complete"

# Explicitly call main function for testing purposes
main("123")
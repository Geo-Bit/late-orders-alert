import requests
import datetime
from google.cloud import secretmanager
from google.cloud import storage
import os
import json
from flask import jsonify

# Initialize the Cloud Storage client
storage_client = storage.Client()
bucket_name = os.getenv('GCS_BUCKET_NAME')
bucket = storage_client.bucket(bucket_name)

# Fulfillment SLA
fulfillment_day_threshold = 7

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
SENDGRID_API_KEY = access_secret("SENDGRID_API_KEY")
print("Accessed SENDGRID_API_KEY from Secret Manager.")

def check_unfulfilled_orders():
    print("Checking for unfulfilled orders...")
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }
    url = f'https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/orders.json'
    params = {
        "status": "open",
        "fulfillment_status": "unfulfilled",
        "created_at_max": (datetime.datetime.now() - datetime.timedelta(days=fulfillment_day_threshold)).isoformat()
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
    if not orders:
        return

    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    sender_email = os.getenv('ALERT_SENDER_EMAIL')
    recipient_emails = [email.strip() for email in os.getenv('ALERT_RECIPIENT_EMAIL').split(',')]

    subject = "Unfulfilled Orders Alert"
    body_lines = [f"The following orders have been unfulfilled for over {fulfillment_day_threshold} days:\n"]
    for order in orders:
        body_lines.append(f"- Order {order['order_number']} (created at: {order['created_at']})\n")

    body_lines.append("\nPlease take necessary actions.")
    body = "".join(body_lines)

    message = Mail(
        from_email=sender_email,
        to_emails=recipient_emails,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("Email alert sent successfully for unfulfilled orders.")
    except Exception as e:
        print(f"Failed to send email alert: {e}")

def main(request):
    print("Starting main function...")
    check_unfulfilled_orders()
    return jsonify({"status": "Check complete"}), 200

# Explicitly call main function for testing purposes
if __name__ == "__main__":
    main(None)
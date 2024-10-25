import requests
import datetime
from google.cloud import secretmanager
import os

def access_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    print(name)
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

SHOPIFY_ACCESS_TOKEN = access_secret("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_NAME = access_secret("SHOPIFY_STORE_NAME")

def check_unfulfilled_orders():
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }
    url = f'https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/orders.json'
    params = {
        "status": "open",
        "fulfillment_status": "unfulfilled",
        "created_at_max": (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()
    }
    response = requests.get(url, headers=headers, params=params)
    print(response)
    orders = response.json().get("orders", [])

    unfulfilled_orders = [
        order for order in orders if not order.get('fulfillment_status')
    ]

    if unfulfilled_orders:
        send_notification(unfulfilled_orders)

def send_notification(orders):
    for order in orders:
        message = f"Order {order['id']} has been unfulfilled for over 10 days."
        print(message)
        # Optionally, integrate with an email or SMS service here

def main():
    check_unfulfilled_orders()
    print ("Check Complete")

if __name__ == "__main__":
    main()
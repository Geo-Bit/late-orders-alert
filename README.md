# Shopify Unfulfilled Orders Alert

This project is a Google Cloud Function that automates the process of checking for unfulfilled Shopify orders and sends notifications if any orders remain unfulfilled for over 10 days. Sensitive credentials are securely stored in Google Secret Manager.

## Prerequisites

- Google Cloud account with Secret Manager and Cloud Functions enabled
- Python 3.x
- Shopify store with API credentials

## Setup Instructions

### 1. Store Secrets in Google Secret Manager

- Navigate to Google Cloud Console and go to **Secret Manager**.
- Create secrets for `SHOPIFY_API_KEY`, `SHOPIFY_PASSWORD`, and `SHOPIFY_STORE_NAME`.

### 2. Grant Access to Secrets

- Go to **IAM & Admin** > **IAM**.
- Locate the service account used by your Cloud Function and add the **Secret Manager Secret Accessor** role.

### 3. Deploy the Cloud Function

- Clone this repository.
- Create a virtual environment and install the required dependencies:
  ```sh
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

## Deploy the Cloud Function

gcloud functions deploy check_unfulfilled_orders --runtime python39 --trigger-http --allow-unauthenticated

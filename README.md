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
- Deploy the Cloud Function
  ```sh
  gcloud functions deploy check_unfulfilled_orders --runtime python39 --trigger-http --allow-unauthenticated --project <GCP_project_name> --service-account <GCP_service_account_name> --env-vars-file .env.yaml
  ```

### 4. Scheduling the Function (Optional)

- Use Google Cloud Scheduler to run the function periodically.

## Files

- `shopify_unfulfilled_orders.py`: Main script for checking unfulfilled orders.

- `requirements.txt`: List of dependencies.

- `.env.yaml` : Contains required environment variables (GOOGLE_CLOUD_PROJECT, GCS_BUCKET_NAME)

- `README.md`: Project documentation.

## Security

Sensitive information is stored in Google Secret Manager, ensuring that credentials are protected and only accessible by authorized services.

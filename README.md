# Shopify Unfulfilled Orders Alert

This project automates monitoring of unfulfilled Shopify orders and sends email alerts when an order remains unfulfilled for a specified number of days. The solution leverages Google Cloud services, including Secret Manager, Cloud Storage, and Cloud Functions, to securely store sensitive information, manage alerts, and run scheduled checks. Alerts are sent as a summary email using Twilio SendGrid, helping to reduce the number of emails while ensuring prompt attention to outstanding orders.

Core features include:

- Secure Credential Storage: Using Google Secret Manager to keep API keys and credentials secure.
- Automated Order Checking: Running scheduled checks on unfulfilled orders using Google Cloud Functions and Cloud Scheduler.
- Alert Management: Tracking previously alerted orders using Google Cloud Storage to avoid duplicate notifications.
- Email Notification: Sending summary alerts to recipients using SendGrid for any orders that have not been fulfilled for the specified time period.

## Prerequisites

- **Google Cloud Project**: Make sure you have a Google Cloud project set up.
- **Secret Manager**: You need to use Google Secret Manager to store sensitive information like API keys, credentials, etc.
- **SendGrid Account**: Set up a SendGrid account to send email alerts.
- **Shopify API Access**: Ensure you have Shopify API credentials to access order information.

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
  gcloud functions deploy check_unfulfilled_orders --runtime python39 --trigger-http --entry-point main --allow-unauthenticated --project <GCP_project_name> --service-account <GCP_service_account_name> --env-vars-file .env.yaml
  ```

### 4. Scheduling the Function (Optional)

- To run the function on a schedule (e.g., twice a day), use Google Cloud Scheduler to trigger the Cloud Function at the desired intervals.

## Files

- `shopify_unfulfilled_orders.py`: Main script for checking unfulfilled orders.

- `requirements.txt`: List of dependencies.

- `.env.yaml` : Contains required environment variables:

  ```yaml
  GOOGLE_CLOUD_PROJECT: <GCP Project ID>
  GCS_BUCKET_NAME: <GCP bucket name>
  ALERT_RECIPIENT_EMAIL: <Comma separated list of recipient emails>
  ALERT_SENDER_EMAIL: <Sender email address>
  ```

- `README.md`: Project documentation.

## Security

Sensitive information is stored in Google Secret Manager, ensuring that credentials are protected and only accessible by authorized services.

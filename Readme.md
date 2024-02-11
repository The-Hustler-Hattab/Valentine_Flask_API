# Valentine Day API

This project is a Flask-based API for a Valentine's Day application. It allows users to upload pictures of themselves or their loved ones, and then performs the following tasks:

1. Detects faces in the uploaded picture using AWS Rekognition.
2. Uses a classification model hosted on Google Cloud Platform (GCP) to determine the identity of the person in the picture.
3. Modifies the picture with a custom quote and sends back a link to the modified picture.

## Features

- Detects faces in pictures.
- Identifies the person in the picture using machine learning classification.
- Adds custom quotes to the pictures.
- Provides a simple and easy-to-use API for integration into other applications.

## Deployment

The project is deployed using Google Cloud Run.

## Prerequisites

Before running the project locally, ensure you have the following prerequisites installed:

- Python 3.8+
- Flask
- boto3 (for AWS Rekognition)
- Google Cloud SDK (for deploying to Google App Engine)

## Setup

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/The-Hustler-Hattab/Valentine_Flask_API.git
   ```
   
2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```
3. Set up AWS credentials and Google Cloud Platform credentials with appropriate permissions for accessing Rekognition and the classification model.
4. Create a .env file in the root directory of your project and add the following environment variables:

    ```bash
   AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
   AWS_REGION=YOUR_AWS_REGION
   S3_BUCKET_NAME=YOUR_S3_BUCKET_NAME
   
   GOOGLE_ENDPOINT_ID=YOUR_GOOGLE_ENDPOINT_ID
   GOOGLE_PROJECT_ID=YOUR_GOOGLE_PROJECT_ID
   GOOGLE_REGION=YOUR_GOOGLE_REGION
   GOOGLE_APPLICATION_CREDENTIALS=ML_KEY.json
   TOGETHER_AI_API_KEY=YOUR_TOGETHER_AI_API_KEY
   
   DEBUG=True
    ```
5. Run the Flask application locally:

    ```bash
    python main.py
    ```
6. Access the API at http://localhost:5000.

## API Endpoints
- /upload: POST endpoint for uploading pictures and receiving modified pictures with custom quotes.

## Usage
- Navigate to swagger documentation at http://localhost:5000/apidocs.
- Send a POST request to the /process-image endpoint with the picture file as a multipart form-data. The API will return a link to the modified picture with a custom quote.


# Deployment Guide for My Flask App

## Step 1: Building the Docker Image

Build the Docker image for the Flask app:

   ```bash
   docker build -t my-flask-app:latest .
   ```

## Step 2: Authenticating with Google Cloud

Ensure you are authenticated with Google Cloud:

   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

## Step 3: Tagging the Docker Image

Tag the Docker image with the appropriate Google Artifact Repository URL. Replace `[Google_Artifact_Repository]` with your actual Google Artifact Repository name.

   ```bash
   docker tag my-flask-app:latest gcr.io/[Google_Artifact_Repository]/my-flask-app:latest
   ```

## Step 4: Pushing the Docker Image to Google Artifact Registry

Push the Docker image to Google Artifact Registry:

   ```bash
   docker push gcr.io/[Google_Artifact_Repository]/my-flask-app:latest
   ```

## Conclusion

Your Flask app image has been successfully pushed to Google Artifact Registry and is ready for deployment.
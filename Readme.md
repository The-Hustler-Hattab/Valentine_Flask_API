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

The project is deployed using Google App Engine.

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

4. Run the Flask application locally:

    ```bash
    python run.py
    ```
5. Access the API at http://localhost:5000.

## API Endpoints
- /upload: POST endpoint for uploading pictures and receiving modified pictures with custom quotes.

## Usage
- Navigate to swagger documentation at http://localhost:5000/apidocs.
- Send a POST request to the /process-image endpoint with the picture file as a multipart form-data. The API will return a link to the modified picture with a custom quote.
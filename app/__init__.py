from flask import Flask
from dotenv import load_dotenv
import os
from flasgger import Swagger


class Constants:
    # AWS
    AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
    AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
    AWS_S3_BUCKET_NAME = 'S3_BUCKET_NAME'
    AWS_REGION = 'AWS_REGION'
    # Google Cloud
    GOOGLE_ENDPOINT_ID = 'GOOGLE_ENDPOINT_ID'
    GOOGLE_PROJECT_ID = 'GOOGLE_PROJECT_ID'
    GOOGLE_REGION = 'GOOGLE_REGION'
    TOGETHER_AI_API_KEY = 'TOGETHER_AI_API_KEY'
    DEBUG = 'DEBUG'


app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
# Set AWS environment variables
app.config[Constants.AWS_ACCESS_KEY_ID] = os.getenv(Constants.AWS_ACCESS_KEY_ID)
app.config[Constants.AWS_SECRET_ACCESS_KEY] = os.getenv(Constants.AWS_SECRET_ACCESS_KEY)
app.config[Constants.AWS_S3_BUCKET_NAME] = os.getenv(Constants.AWS_S3_BUCKET_NAME)
app.config[Constants.AWS_REGION] = os.getenv(Constants.AWS_REGION)

# Set Google environment variables
app.config[Constants.GOOGLE_ENDPOINT_ID] = os.getenv(Constants.GOOGLE_ENDPOINT_ID)
app.config[Constants.GOOGLE_PROJECT_ID] = os.getenv(Constants.GOOGLE_PROJECT_ID)
app.config[Constants.GOOGLE_REGION] = os.getenv(Constants.GOOGLE_REGION)

app.config[Constants.TOGETHER_AI_API_KEY] = os.getenv(Constants.TOGETHER_AI_API_KEY)

# Set debug environment variable
app.config[Constants.DEBUG] = os.getenv(Constants.DEBUG)

# load swagger
swagger = Swagger(app)

# Import routes after creating the app instance to avoid circular imports
from app import routes

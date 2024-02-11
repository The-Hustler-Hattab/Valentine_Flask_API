from werkzeug.datastructures import FileStorage

from app import app
from flask import request, jsonify
from app.utils.utils import Utils

from app.service.image_service import ImageService, ManipulateImageService


@app.route('/')
def index() -> str:
    """
    Home endpoint.
    ---
    responses:
      200:
        description: A simple Hello World message.
    """
    return 'Hello, World!'


@app.route('/process-image', methods=['POST'])
def manipulate_image():
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    # Get the file from the request
    file: FileStorage = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected image file'}), 400

    # process the image
    return ManipulateImageService.manipulate_image(file)

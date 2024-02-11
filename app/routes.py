from typing import Tuple, Dict

from werkzeug.datastructures import FileStorage

from app import app
from flask import request, jsonify, redirect

from app.service.image_service import ManipulateImageService


@app.route('/health')
def health() -> Tuple[Dict[str, str], int]:
    """
    Health Check Endpoint.
    ---
    responses:
      200:
        description: OK if the service is healthy.
    """
    return {'status': 'OK',
            'msg': 'API is up'}, 200


@app.route('/process-image', methods=['POST'])
def manipulate_image():
    """
    Endpoint to process an image.
    ---
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The image file to be processed.
    responses:
      200:
        description: The processed image.
      400:
        description: Bad request if no image is provided or no image file is selected.
    """
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    # Get the file from the request
    file: FileStorage = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected image file'}), 400

    # process the image
    return ManipulateImageService.manipulate_image(file)


# Custom 404 error handler
@app.errorhandler(404)
def not_found(error):
    # Redirect to Swagger UI page
    return redirect('/apidocs')

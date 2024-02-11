from werkzeug.datastructures import FileStorage

from app import app
from flask import request, jsonify
from app.utils.utils import Utils

from app.service.image_service import ImageService, ManipulateImageService



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

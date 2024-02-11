import datetime
import os
from typing import Any, Dict, List, Tuple

from PIL import Image

import io
import base64

from werkzeug.datastructures import FileStorage

from app.model.prediction_model import PredictionModel
import cv2
import numpy as np


class Utils:

    @staticmethod
    def pre_append_date(file: str) -> str:
        # Prepend current date to the filename
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        filename_with_date = f"{current_date}_{file}"
        return filename_with_date

    @staticmethod
    def create_dir(directory_path: str) -> None:
        if not os.path.exists(directory_path):
            # Create the directory
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        else:
            print(f"Directory '{directory_path}' already exists.")

    @staticmethod
    def save_file_locally(file: FileStorage) -> Tuple[str, str]:
        # Save the image to a temporary file
        # Define the path for the new directory
        directory_path = "./tmp"
        # Check if the directory already exists
        Utils.create_dir(directory_path)
        file_name = Utils.pre_append_date(file.filename)
        file_path = f'{directory_path}/' + file_name
        file.save(file_path)
        return file_name, file_path

    @staticmethod
    def prepare_image(file_path: str, output_size=(800, 600), quality=85):
        # Open the image
        with Image.open(file_path) as img:
            # Resize the image, maintaining aspect ratio
            img.thumbnail(output_size)

            # If the image is in RGBA mode (has an alpha channel), convert it to RGB
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Save the image to a bytes buffer with compression
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)

            # Encode the modified image to base64
            encoded_image = base64.b64encode(buffer.read()).decode("utf-8")

        return encoded_image

    @staticmethod
    def read_binary_file(file_path: str):
        """
        Reads the content of a binary file (e.g., an image) given its file path.

        :param file_path: Path to the binary file.
        :return: Content of the file in binary format.
        """
        try:
            with open(file_path, 'rb') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading binary file: {e}")
            return None

    @staticmethod
    def convert_dict_to_list_of_models(prediction_dict: Dict[str, Any]) -> List[PredictionModel]:
        # Convert the dictionary into a list of PredictionModel instances
        prediction_models: List[PredictionModel] = [
            PredictionModel(label, confidence, _id)
            for label, confidence, _id in
            zip(prediction_dict['displayNames'], prediction_dict['confidences'], prediction_dict['ids'])
        ]
        # Sort the list by confidence score
        prediction_models.sort(key=lambda x: x.prediction_confidence, reverse=True)
        return prediction_models

    @staticmethod
    def add_cigar_and_sunglasses(image_path: str, face_details: dict, sunglasses_scale_factor: float = 2.3) -> str:
        # Load the image
        image = cv2.imread(image_path)

        # Define the paths to the accessories
        sunglasses_path = "app/static/Sunglasses.png"
        cigar_path = "app/static/cigar.png"

        # Read the accessory images with transparency
        sunglasses = cv2.imread(sunglasses_path, cv2.IMREAD_UNCHANGED)
        cigar = cv2.imread(cigar_path, cv2.IMREAD_UNCHANGED)

        # Extract face landmarks
        left_eye = face_details['landmarks'][0]
        right_eye = face_details['landmarks'][1]
        mouth_left = face_details['landmarks'][2]
        mouth_right = face_details['landmarks'][3]

        # Calculate the center coordinates of each eye
        left_eye_center = (int(left_eye['X'] * image.shape[1]), int(left_eye['Y'] * image.shape[0]))
        right_eye_center = (int(right_eye['X'] * image.shape[1]), int(right_eye['Y'] * image.shape[0]))

        # Position sunglasses based in the center of each eye
        sunglasses_width = (right_eye_center[0] - left_eye_center[0]) * sunglasses_scale_factor
        sunglasses_height = (sunglasses.shape[0] * sunglasses_width // sunglasses.shape[1]) * sunglasses_scale_factor
        sunglasses_resized = cv2.resize(sunglasses, (int(sunglasses_width), int(sunglasses_height)))
        x_offset = left_eye_center[0] - int(sunglasses_width * 0.2)  # Move sunglasses to the left a little bit
        y_offset = left_eye_center[1] - sunglasses_resized.shape[0] // 2
        image_with_sunglasses = Utils.overlay_transparent(image, sunglasses_resized, (x_offset, y_offset))

        # Calculate the position of the cigar
        cigar_width = mouth_right['X'] * image.shape[1] - mouth_left['X'] * image.shape[1]
        cigar_height = cigar.shape[0] * cigar_width // cigar.shape[1]
        cigar_resized = cv2.resize(cigar, (int(cigar_width), int(cigar_height)))
        x_offset = int(mouth_left['X'] * image.shape[1])
        y_offset = int(mouth_left['Y'] * image.shape[0]) - int(cigar_height * 0.2)  # Move cigar up a little bit
        image_with_accessories = Utils.overlay_transparent(image_with_sunglasses, cigar_resized, (x_offset, y_offset))

        # Save the modified image
        output_path = "tmp/output_image_with_accessories.jpg"
        cv2.imwrite(output_path, image_with_accessories)

        return output_path
    @staticmethod
    def add_hearts_on_eyes(image_path: str, face_details: dict, heart_scale_factor: float = 0.8) -> str:
        # Load the image
        image = cv2.imread(image_path)

        # Define the path to the heart image
        heart_path = "app/static/sapphire_heart.png"

        # Read the heart image with transparency
        heart = cv2.imread(heart_path, cv2.IMREAD_UNCHANGED)

        # Extract face landmarks for left and right eyes
        left_eye = face_details['landmarks'][0]
        right_eye = face_details['landmarks'][1]

        # Calculate the center coordinates of each eye
        left_eye_center = (int(left_eye['X'] * image.shape[1]), int(left_eye['Y'] * image.shape[0]))
        right_eye_center = (int(right_eye['X'] * image.shape[1]), int(right_eye['Y'] * image.shape[0]))

        # Resize the heart image
        heart_width = int((right_eye_center[0] - left_eye_center[0]) * heart_scale_factor)
        heart_height = int(heart.shape[0] * heart_width / heart.shape[1])
        heart_resized = cv2.resize(heart, (heart_width, heart_height))

        # Position the heart on the left eye
        x_offset_left_eye = left_eye_center[0] - int(heart_width * 0.5)
        y_offset_left_eye = left_eye_center[1] - int(heart_height * 0.5)
        image_with_hearts = Utils.overlay_transparent(image, heart_resized, (x_offset_left_eye, y_offset_left_eye))

        # Position the heart on the right eye
        x_offset_right_eye = right_eye_center[0] - int(heart_width * 0.5)
        y_offset_right_eye = right_eye_center[1] - int(heart_height * 0.5)
        image_with_hearts = Utils.overlay_transparent(image_with_hearts, heart_resized,
                                                (x_offset_right_eye, y_offset_right_eye))

        # Save the modified image
        output_path = "tmp/output_image_with_hearts.jpg"
        cv2.imwrite(output_path, image_with_hearts)

        return output_path

    @staticmethod
    def overlay_transparent(background, overlay, location):
        """
        Overlay a transparent image onto another image.
        """
        x, y = location

        # Check overlay dimensions
        if overlay.shape[:2] != background[y:y + overlay.shape[0], x:x + overlay.shape[1]].shape[:2]:
            raise ValueError("Overlay dimensions do not match the region of interest")

        # Cut the region of interest from the background
        foreground = background[y:y + overlay.shape[0], x:x + overlay.shape[1]]

        # If overlay has an alpha channel, use it for blending
        if overlay.shape[2] == 4:
            # Extract alpha channel
            alpha = overlay[:, :, 3] / 255.0

            # Perform alpha blending
            blended = np.empty_like(foreground, dtype=np.uint8)
            for c in range(3):  # Iterate over RGB channels
                blended[..., c] = overlay[..., c] * alpha + foreground[..., c] * (1 - alpha)

            # Update the region of interest
            background[y:y + overlay.shape[0], x:x + overlay.shape[1]] = blended
        else:
            # If overlay does not have an alpha channel, assume it's fully opaque
            background[y:y + overlay.shape[0], x:x + overlay.shape[1]] = overlay

        return background

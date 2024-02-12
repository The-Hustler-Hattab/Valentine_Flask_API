from typing import Tuple, Dict, List, Any, MutableSequence, Optional

import boto3
from flask import jsonify, Response
from google.cloud.aiplatform_v1 import PredictResponse
from werkzeug.datastructures import FileStorage

from app import Constants, app
from app.model.prediction_model import PredictionModel
from app.utils.utils import Utils
from app.service.llm_service import LLMService

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf.json_format import MessageToDict
import os
from PIL import Image

# Initialize S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=app.config.get(Constants.AWS_ACCESS_KEY_ID),
                  aws_secret_access_key=app.config.get(Constants.AWS_SECRET_ACCESS_KEY))
# Initialize Rekognition client
rekognition = boto3.client('rekognition',
                           aws_access_key_id=app.config.get(Constants.AWS_ACCESS_KEY_ID),
                           aws_secret_access_key=app.config.get(Constants.AWS_SECRET_ACCESS_KEY),
                           region_name=app.config.get(Constants.AWS_REGION))


class ImageService:
    # AWS
    aws_s3_bucket_name = app.config.get(Constants.AWS_S3_BUCKET_NAME)
    aws_s3_base_url = f"https://{aws_s3_bucket_name}.s3.amazonaws.com/"

    # Google Cloud
    google_project_id = app.config.get(Constants.GOOGLE_PROJECT_ID)
    google_endpoint_id = app.config.get(Constants.GOOGLE_ENDPOINT_ID)
    google_region = app.config.get(Constants.GOOGLE_REGION)

    mary_prompt = (
        'My dear princess your eyes hold a universe of love, kindness, and compassion. I am grateful every '
        'day to be able to look into them')
    mohammed_prompt = (
        'I promise to be your protector and provider, supporting you through every moment. You mean the '
        'world to me.')

    # Initialize the prediction client as a class-level variable
    prediction_client = None

    @staticmethod
    def upload_image_to_s3(file_name, file_path) -> Tuple[str, str, str]:
        # Upload the image to S3
        s3.upload_file(file_path, ImageService.aws_s3_bucket_name, file_name, ExtraArgs={'ACL': 'public-read'})

        # Generate the full URL for the uploaded image
        image_url = ImageService.aws_s3_base_url + file_name

        return image_url

    @staticmethod
    def call_facial_detector_api(file_path: str) -> Tuple[Any, List[Dict[str, Any]]]:
        # Load the image data
        image_data = Utils.read_binary_file(file_path)

        # Call Rekognition API to detect faces
        response = rekognition.detect_faces(
            Image={'Bytes': image_data},
            Attributes=['GENDER']  # Change attributes as needed, 'ALL' will return all available attributes
        )
        print(response)
        list_of_faces = ImageService.extract_faces_and_save(file_path, response)
        # Return the response from the API
        return response, list_of_faces

    @staticmethod
    def extract_faces_and_save(original_image_path: str, recognition_api_output: dict, output_folder: str = "tmp/faces",
                               scale_factor: float = 1.2) -> List[Dict[str, Any]]:
        """
        Extracts faces from the original image based on the bounding box coordinates provided
        in the recognition API output, scales them, and saves each face as a separate image
        in the specified output folder.

        Parameters:
            original_image_path (str): Path to the original image file.
            recognition_api_output (dict): Recognition API output containing face details.
            output_folder (str, optional): Path to the folder where the extracted faces will be saved. Default is "faces".
            scale_factor (float, optional): Scale factor by which to resize the extracted face. Default is 1.2.

        Returns:
            List[str]: List of file paths where the extracted faces are saved.
        """
        list_of_faces = []
        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Load the original image
        original_image = Image.open(original_image_path)

        # Loop through each face detail in the response
        for idx, face_detail in enumerate(recognition_api_output["FaceDetails"]):
            # Get the bounding box coordinates
            bounding_box = face_detail["BoundingBox"]
            left = int(bounding_box["Left"] * original_image.width)
            top = int(bounding_box["Top"] * original_image.height)
            width = int(bounding_box["Width"] * original_image.width)
            height = int(bounding_box["Height"] * original_image.height)

            # Scale the bounding box dimensions
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            new_left = max(left - (new_width - width) // 2, 0)
            new_top = max(top - (new_height - height) // 2, 0)

            # Crop the scaled face from the original image
            face_image = original_image.crop((new_left, new_top, new_left + new_width, new_top + new_height))

            # Save the cropped face as a new image
            original_image_name = os.path.splitext(os.path.basename(original_image_path))[0]
            face_image_path = os.path.join(output_folder, f"{original_image_name}_{idx}.jpg")
            if face_image.mode == 'RGBA':
                face_image = face_image.convert('RGB')

            face_image.save(face_image_path)
            face_info_dict: Dict[str, Any] = {
                "face_image_path": face_image_path,
                "bounding_box": bounding_box,
                "gender": face_detail['Gender']['Value'],
                "landmarks": face_detail['Landmarks']
            }
            list_of_faces.append(face_info_dict)
            print(f"Face {idx + 1} saved as {face_image_path}")
        return list_of_faces

    @staticmethod
    def initialize_prediction_client() -> None:
        if not ImageService.prediction_client:
            # Initialize PredictionServiceClient
            client_options = {"api_endpoint": f"{ImageService.google_region}-aiplatform.googleapis.com"}
            ImageService.prediction_client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    @staticmethod
    def call_classifier_api(file_path) -> List[PredictionModel]:
        # Initialize the prediction client if not already initialized
        ImageService.initialize_prediction_client()
        print(f"file_path: {file_path}")
        # file must be encoded to base64
        encoded_content = Utils.prepare_image(file_path)

        # Prepare the request payload. The format of each instance should conform to the deployed model's prediction
        # input schema.
        instance = predict.instance.ImageClassificationPredictionInstance(
            content=encoded_content,
        ).to_value()

        instances = [instance]
        parameters = predict.params.ImageClassificationPredictionParams(
            confidence_threshold=0.5,
            max_predictions=1,
        ).to_value()

        # Prepare the endpoint name
        endpoint = ImageService.prediction_client.endpoint_path(project=ImageService.google_project_id,
                                                                location=ImageService.google_region,
                                                                endpoint=ImageService.google_endpoint_id)

        # Make the prediction request
        response: PredictResponse = ImageService.prediction_client.predict(
            instances=instances,
            parameters=parameters,
            endpoint=endpoint,

        )
        # the api will return a Google protocol buffer which we need to convert to a dictionary
        proto_buf = response.predictions.__dict__['_pb'][0]
        protobuf_dict = MessageToDict(proto_buf)

        return Utils.convert_dict_to_list_of_models(protobuf_dict)


class ManipulateImageService:
    @staticmethod
    def manipulate_image(file: FileStorage) -> Tuple[Response, int]:
        file_name, file_path = Utils.save_file_locally(file)
        # save the original image to s3
        ImageService.upload_image_to_s3(f'original_{file_name}', file_path)
        # get face details
        recognition_api_output, list_of_faces = ImageService.call_facial_detector_api(file_path)
        # check if there are faces in the image
        if not list_of_faces:
            return jsonify({'msg': 'No faces detected in the image'}), 400
        else:
            return ManipulateImageService.process_image_with_faces(file_name, file_path, list_of_faces)

    @staticmethod
    def process_image_with_faces(file_name: str, file_path: str, list_of_faces: List[Dict]):
        # if there are faces, call the classifier api for each face
        face_with_highest_confidence_that_is_not_unknown: Optional[
            PredictionModel] = ManipulateImageService.get_face_with_highest_confidence(list_of_faces)
        if face_with_highest_confidence_that_is_not_unknown is None:
            return jsonify({'msg': 'No known face detected'}), 400
        elif (face_with_highest_confidence_that_is_not_unknown.prediction_label == 'Mary' and
              face_with_highest_confidence_that_is_not_unknown.face_details["gender"] != 'Female') \
                or (face_with_highest_confidence_that_is_not_unknown.prediction_label == 'Mohammed' and
                    face_with_highest_confidence_that_is_not_unknown.face_details["gender"] != 'Male'):
            return jsonify({'msg': 'No known face detected'}), 400
        else:
            return ManipulateImageService.process_known_face(file_name, file_path,
                                                             face_with_highest_confidence_that_is_not_unknown)

    @staticmethod
    def process_known_face(file_name: str, file_path: str,
                           face_with_highest_confidence_that_is_not_unknown: PredictionModel):
        print(f'face_with_highest_confidence_that_is_not_unknown: {face_with_highest_confidence_that_is_not_unknown}')
        image_url = None
        msg = 'NA'
        llm_prompt = 'Reword the following sentence: {}'

        modified_file_name = f'modified_{file_name}'
        modified_file_path = ''
        if face_with_highest_confidence_that_is_not_unknown.prediction_label == 'Mary':
            modified_file_path = Utils.add_hearts_on_eyes(file_path,
                                                          face_with_highest_confidence_that_is_not_unknown.face_details)

            ImageService.mary_prompt = LLMService.get_response(llm_prompt.format(ImageService.mary_prompt))

            msg = ImageService.mary_prompt

            # Use the service class to upload the image
            image_url = ImageService.upload_image_to_s3(modified_file_name,
                                                        modified_file_path)
        elif face_with_highest_confidence_that_is_not_unknown.prediction_label == 'Mohammed':
            modified_file_path = Utils.add_cigar_and_sunglasses(file_path,
                                                                face_with_highest_confidence_that_is_not_unknown.face_details)

            ImageService.mohammed_prompt = LLMService.get_response(llm_prompt.format(ImageService.mohammed_prompt))
            msg = ImageService.mohammed_prompt

            # Use the service class to upload the image
            image_url = ImageService.upload_image_to_s3(modified_file_name,
                                                        modified_file_path)

        os.remove(file_path)
        os.remove(face_with_highest_confidence_that_is_not_unknown.face_image_path)
        os.remove(modified_file_path)
        # Return the image URL as JSON
        return jsonify({'imageUrl': image_url,
                        'predictionLabel': face_with_highest_confidence_that_is_not_unknown.prediction_label,
                        'msg': msg}), 200

    # this method will return the face with the highest confidence that is not unknown. it will also return the face
    # details along with the prediction
    @staticmethod
    def get_face_with_highest_confidence(list_of_faces: List[dict]) -> Optional[PredictionModel]:
        face_with_highest_confidence_that_is_not_unknown = None
        highest_confidence = -1

        for face in list_of_faces:
            face_image_path = face["face_image_path"]
            google_classifier_api_output: List[PredictionModel] = ImageService.call_classifier_api(face_image_path)
            for e in google_classifier_api_output:
                print(e)

            if google_classifier_api_output and google_classifier_api_output[0].prediction_label != 'Unknown':
                if google_classifier_api_output[0].prediction_confidence > highest_confidence:
                    highest_confidence = google_classifier_api_output[0].prediction_confidence
                    face_with_highest_confidence_that_is_not_unknown = google_classifier_api_output[0]
                    face_with_highest_confidence_that_is_not_unknown.face_details = face
                    face_with_highest_confidence_that_is_not_unknown.face_image_path = face_image_path
                else:
                    os.remove(face_image_path)

        return face_with_highest_confidence_that_is_not_unknown

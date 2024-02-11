from typing import Dict, Any


class PredictionModel:
    prediction_label: str
    prediction_confidence: float
    prediction_id: float

    face_details: Dict[str, Any] = {}
    face_image_path: str = ''

    def __init__(self, prediction_label: str, prediction_confidence: float, prediction_id: float):
        self.prediction_label = prediction_label
        self.prediction_confidence = prediction_confidence
        self.prediction_id = prediction_id

    def __str__(self):
        return f"PredictionModel(label={self.prediction_label}, confidence={self.prediction_confidence}, id={self.prediction_id}, face_image_path={self.face_image_path}, face_details={self.face_details})"

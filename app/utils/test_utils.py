from datetime import datetime
from unittest import TestCase

from app.model.prediction_model import PredictionModel
from app.utils.utils import Utils


class TestUtils(TestCase):

    def test_convert_dict_to_list_of_models(self):
        prediction_dict = {
            'displayNames': ['Mary', 'Unknown'],
            'confidences': [0.473895788, 0.504863381],
            'ids': ['2141516873273966592', '5266909461552824320']
        }

        expected_models = [
            PredictionModel('Unknown', 0.504863381, '5266909461552824320'),
            PredictionModel('Mary', 0.473895788, '2141516873273966592'),
        ]

        # Call the method being tested
        result_models = Utils.convert_dict_to_list_of_models(prediction_dict)
        for result_model in result_models:
            print(result_model)

        # Assert that the result matches the expected output
        self.assertEqual(len(result_models), len(expected_models))
        for result, expected in zip(result_models, expected_models):
            self.assertEqual(result.prediction_label, expected.prediction_label)
            self.assertEqual(result.prediction_confidence, expected.prediction_confidence)
            self.assertEqual(result.prediction_id, expected.prediction_id)

    def test_pre_append_date(self):
        # Test case 1: Test with a sample file name
        sample_file = "example.jpg"
        expected_result = f"{datetime.now().strftime('%Y-%m-%d')}_{sample_file}"
        result = Utils.pre_append_date(sample_file)
        print(f"result: {result}")
        self.assertEqual(result, expected_result)

        # Test case 2: Test with a different sample file name
        sample_file_2 = "another_example.png"
        expected_result_2 = f"{datetime.now().strftime('%Y-%m-%d')}_{sample_file_2}"
        result_2 = Utils.pre_append_date(sample_file_2)
        print(f"result_2: {result_2}")

        self.assertEqual(result_2, expected_result_2)

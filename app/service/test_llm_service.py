from unittest import TestCase

from app.service.llm_service import LLMService


class TestLLMService(TestCase):


    def test_get_response(self):
        response = LLMService.get_response("Hello, World!")
        print(response)
        # self.fail()

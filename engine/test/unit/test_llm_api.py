# import pytest
# from unittest.mock import patch
# from app.services.llm_api import get_mapping


# @pytest.mark.parametrize(
#     "use_openai, expected", [(False, "mocked JSONata"), (True, "$")]
# )
# @patch("app.services.llm_api.get_groq_mapping")
# @patch("app.services.llm_api.get_openai_mapping")
# def test_get_mapping(mock_openai, mock_groq, use_openai, expected):
#     """Test that get_mapping correctly routes requests to the right function."""
#     mock_openai.return_value = "$"
#     mock_groq.return_value = "mocked JSONata"

#     messages = [{"role": "user", "content": "Convert this"}]
#     result = get_mapping(messages, use_openai)

#     assert result == expected
#     if use_openai:
#         mock_openai.assert_called_once()
#     else:
#         mock_groq.assert_called_once()

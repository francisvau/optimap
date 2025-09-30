# from app.services.prompt_builder import create_prompt


# def test_create_prompt():
#     """Test prompt creation with valid schemas."""
#     input_schema = {"name": "string"}
#     output_schema = {"full_name": "string"}

#     messages = create_prompt(input_schema, output_schema)

#     assert isinstance(messages, list)
#     assert len(messages) == 2
#     assert "role" in messages[0]
#     assert messages[0]["role"] == "system"
#     assert "role" in messages[1]
#     assert messages[1]["role"] == "user"
#     assert "Convert the following input JSON schema" in messages[1]["content"]

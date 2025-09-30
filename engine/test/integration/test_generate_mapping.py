# from fastapi.testclient import TestClient
# from app.main import app

# client = TestClient(app)


# def test_generate_basic_mapping():
#     """Test the generate_mapping endpoint."""

#     payload = {
#         "input_schema": {"firstName": "string"},
#         "output_schema": {"name": "string"},
#     }
#     response = client.post("/base/generate-mapping", json=payload)
#     assert response.status_code == 200
#     assert "jsonata_mapping" in response.json()

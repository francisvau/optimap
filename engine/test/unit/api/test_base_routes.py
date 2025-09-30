# from fastapi.testclient import TestClient
# from fastapi import status


# def test_generate_mapping(client: TestClient):
#     """Test the generate_mapping endpoint with real transformation logic"""
#     # Arrange
#     payload = {
#         "input_schema": {"name": "string"},
#         "output_schema": {"fullName": "string"},
#     }

#     # Act
#     response = client.post("/base/generate-mapping", json=payload)

#     # Assert
#     assert response.status_code == 200
#     result = response.json()
#     assert "jsonata_mapping" in result

#     # Validate basic JSONata structure
#     assert "name" in result["jsonata_mapping"]
#     assert "fullName" in result["jsonata_mapping"]


# def test_full_blueprint_lifecycle(client: TestClient):
#     """Test complete CRUD lifecycle for blueprints"""
#     # Test Create
#     payload = {
#         "input_schema": {"username": "string"},
#         "output_schema": {"user": {"name": "string"}},
#         "mapping": "{ 'user': { 'name': username } }",
#     }

#     # Create blueprint
#     create_response = client.post("/base/blueprints", json=payload)
#     assert create_response.status_code == 200
#     blueprint_id = create_response.json()
#     assert len(blueprint_id) == 24  # MongoDB ID length validation

#     # Test Read
#     get_response = client.get(f"/base/blueprints/{blueprint_id}")
#     assert get_response.status_code == 200
#     blueprint = get_response.json()

#     assert blueprint["_id"] == blueprint_id
#     assert blueprint["input_schema"] == payload["input_schema"]
#     assert blueprint["output_schema"] == payload["output_schema"]
#     assert blueprint["mapping"] == payload["mapping"]

#     # Test Update (not yet implemented)
#     # updated_mapping = "{ 'user': { 'fullName': username } }"
#     # update_response = client.post(
#     #     f"/base/blueprints/{blueprint_id}", json={"mapping": updated_mapping}
#     # )
#     # assert update_response.status_code == status.HTTP_501_NOT_IMPLEMENTED

#     # updated_get_response = client.get(f"/base/blueprints/{blueprint_id}")
#     # assert updated_get_response.json()["mapping"] == updated_mapping

#     # Test Delete
#     delete_response = client.delete(f"/base/blueprints/{blueprint_id}")
#     assert delete_response.status_code == status.HTTP_200_OK
#     assert delete_response.json()["deleted_count"] == 1

#     # Verify deletion
#     get_deleted_response = client.get(f"/base/blueprints/{blueprint_id}")
#     assert get_deleted_response.status_code == 404


# def test_edit_mapping():
#     """Test the edit_mapping endpoint."""

#     # TODO: Implement this test
#     pass


# def test_get_explanation():
#     """Test the get_explanation endpoint."""

#     # TODO: Implement this test
#     pass

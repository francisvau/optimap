import io
import json

from fastapi import status
from httpx import AsyncClient

"""
Schema Extraction
"""


async def test_schema_extraction_csv(async_client: AsyncClient) -> None:
    """Test schema extraction from a CSV file."""
    file = (
        "test.csv",
        io.BytesIO(
            "\n".join(
                [
                    '"first_name","last_name","created_at"',
                    '"Alice","Smith","12/03/2024"',
                ]
            ).encode()
        ),
        "text/csv",
    )

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files={"file": file}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "items" in response.json()["jsonSchema"]
    assert "properties" in response.json()["jsonSchema"]["items"]
    assert response.json()["jsonSchema"]["items"]["properties"]["created_at"][
        "examples"
    ] == [
        "12/03/2024",
    ]


async def test_schema_extraction_xml(async_client: AsyncClient) -> None:
    """Test schema extraction from an XML file."""
    xml_data = "<root><user><first_name>Alice</first_name><last_name>Smith</last_name><created_at>12/03/2024</created_at></user></root>"

    # Create a file-like object with the XML data
    file = ("test.xml", io.BytesIO(xml_data.encode()), "application/xml")

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files={"file": file}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "items" in response.json()["jsonSchema"]
    assert "properties" in response.json()["jsonSchema"]["items"]
    assert response.json()["jsonSchema"]["items"]["properties"]["first_name"][
        "examples"
    ] == ["Alice"]
    assert response.json()["jsonSchema"]["items"]["properties"]["last_name"][
        "examples"
    ] == ["Smith"]


async def test_schema_extraction_xml_2(async_client: AsyncClient) -> None:
    """Test schema extraction from an XML file."""
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <order>
        <order_key>order_abc123</order_key>
        <date_created_gmt>2025-05-07T10:30:00Z</date_created_gmt>
        <line_items>
            <item>
                <product_id>prod001</product_id>
                <qty>2</qty>
                <price>19.99</price>
            </item>
            <item>
                <product_id>prod002</product_id>
                <qty>1</qty>
                <price>49.99</price>
            </item>
        </line_items>
        <customer_message>Please deliver between 3–5 PM. Leave at the front desk if not home.</customer_message>
    </order>"""

    # Create a file-like object with the XML data
    file = ("test.xml", io.BytesIO(xml_data.encode()), "application/xml")

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files={"file": file}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "items" in response.json()["jsonSchema"]
    assert "properties" in response.json()["jsonSchema"]["items"]
    assert (
        "price"
        in response.json()["jsonSchema"]["items"]["properties"]["line_items"]["items"][
            "properties"
        ]
    )


async def test_schema_extraction_single_object(async_client: AsyncClient) -> None:
    """Test schema extraction from a single JSON object."""
    json_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "created_at": "12/03/2024",
    }

    # Create a file-like object with the JSON data
    file_content = json.dumps(json_data).encode()
    files = {"file": ("test.json", io.BytesIO(file_content), "application/json")}

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files=files
    )

    assert response.status_code == status.HTTP_200_OK
    assert "properties" in response.json()["jsonSchema"]
    assert response.json()["jsonSchema"]["properties"]["created_at"]["examples"] == [
        "12/03/2024",
    ]


async def test_schema_extraction_sql(async_client: AsyncClient) -> None:
    """Test schema extraction from an SQL file with INSERT statements."""
    sql_data = """
    INSERT INTO users (first_name, last_name, created_at) VALUES
    ('Alice', 'Smith', '12/03/2024');
    """

    file = ("test.sql", io.BytesIO(sql_data.encode()), "application/sql")

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files={"file": file}
    )

    assert response.status_code == status.HTTP_200_OK
    schema = response.json()["jsonSchema"]

    assert "items" in schema
    assert "properties" in schema["items"]
    assert schema["items"]["properties"]["created_at"]["examples"] == [
        "12/03/2024",
    ]


async def test_schema_extraction_sql_2(async_client: AsyncClient) -> None:
    """Test schema extraction from an SQL file with INSERT statements."""
    sql_data = """
    -- Orders table creation
    CREATE TABLE orders (
        order_id VARCHAR(50) PRIMARY KEY,
        date_created_gmt TIMESTAMP,
        customer_message TEXT
    );

    -- Order line items table creation
    CREATE TABLE order_line_items (
        line_item_id SERIAL PRIMARY KEY,
        order_id VARCHAR(50) REFERENCES orders(order_id),
        product_id VARCHAR(50),
        qty INTEGER,
        price DECIMAL(10,2)
    );

    -- Insert the order data
    INSERT INTO orders (order_id, date_created_gmt, customer_message)
    VALUES (
        'order_abc123',
        '2025-05-07 10:30:00',
        'Please deliver between 3–5 PM. Leave at the front desk if not home.'
    );

    -- Insert the line items
    INSERT INTO order_line_items (order_id, product_id, qty, price)
    VALUES
        ('order_abc123', 'prod001', 2, 19.99),
        ('order_abc123', 'prod002', 1, 49.99);
    """

    file = ("test.sql", io.BytesIO(sql_data.encode()), "application/sql")

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files={"file": file}
    )

    assert response.status_code == status.HTTP_200_OK
    schema = response.json()["jsonSchema"]

    assert "items" in schema
    assert "properties" in schema["items"]
    assert schema["items"]["properties"]["date_created_gmt"]["examples"] == [
        "2025-05-07 10:30:00",
    ]


async def test_schema_extraction_multiple_objects(async_client: AsyncClient) -> None:
    """Test schema extraction from a list of JSON objects with mixed types."""
    json_data = [
        {"first_name": "Alice", "created_at": "12/03/2024"},
        {"first_name": "Bob", "created_at": "12/04/2024"},
    ]

    # Create a file-like object with the JSON data
    file_content = json.dumps(json_data).encode()
    files = {"file": ("test.json", io.BytesIO(file_content), "application/json")}

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files=files
    )
    assert response.status_code == status.HTTP_200_OK
    props = response.json()["jsonSchema"]["items"]["properties"]
    assert "created_at" in props
    assert "examples" in props["created_at"]
    assert props["created_at"]["examples"] == ["12/03/2024", "12/04/2024"]


async def test_schema_extraction_invalid_data(async_client: AsyncClient) -> None:
    """Test schema extraction with invalid data (not valid JSON)."""
    # Create a file with invalid JSON content
    file_content = "this is not a valid JSON object".encode()
    files = {"file": ("test.json", io.BytesIO(file_content), "application/json")}

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files=files
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_schema_extraction_array_data(async_client: AsyncClient) -> None:
    data = [
        {
            "order_id": "ORD-20250508-042",
            "order_date": "2025-05-08",
            "customer_email": "alice.wonderland@example.com",
            "shipping_method": "overnight",
            "items": [
                {"product_sku": "SKU-001", "qty_ordered": 2, "price_per_unit": 19.99},
                {"product_sku": "SKU-002", "qty_ordered": 1, "price_per_unit": 49.5},
                {"product_sku": "SKU-123-X", "qty_ordered": 5, "price_per_unit": 3.75},
            ],
            "notes": "Please include a handwritten thank-you note and gift wrap all items separately.",
            "shipping_address": {
                "street_address": "789 Elm Street, Apt. 5B",
                "city": "Ghent",
                "postal_code": "9000",
                "country": "BE",
            },
        },
        {
            "order_id": "ORD-20250508-044",
            "order_date": "2025-07-10",
            "customer_email": "thomas.bright@example.com",
            "shipping_method": "standard",
            "items": [
                {"product_sku": "SKU-001", "qty_ordered": 2, "price_per_unit": 19.99},
                {"product_sku": "SKU-002", "qty_ordered": 1, "price_per_unit": 49.5},
            ],
            "shipping_address": {
                "street_address": "789 Elm Street, Apt. 5B",
                "city": "Ghent",
                "postal_code": "9000",
                "country": "BE",
            },
        },
    ]

    # Create a file-like object with the JSON data
    file_content = json.dumps(data).encode()
    files = {"file": ("test.json", io.BytesIO(file_content), "application/json")}

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files=files
    )

    json_response = response.json()

    assert "items" in json_response["jsonSchema"]
    assert json_response["jsonSchema"]["items"]["type"] == "object"
    assert "properties" in json_response["jsonSchema"]["items"]
    assert json_response["jsonSchema"]["type"] == "array"
    assert response.status_code == status.HTTP_200_OK


async def test_schema_extraction_unsupported_type(async_client: AsyncClient) -> None:
    """Test schema extraction with an unsupported file type."""
    file_content = "some content".encode()
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files=files
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported file type" in response.json()["detail"]


async def test_schema_extraction_file_too_large(async_client: AsyncClient) -> None:
    """Test schema extraction with a file that exceeds the size limit."""
    # Create a file that's larger than 30MB
    file_content = b"x" * (31 * 1024 * 1024)  # 31MB
    files = {"file": ("test.json", io.BytesIO(file_content), "application/json")}

    response = await async_client.post(
        "/mappings/schema/schema-extraction", files=files
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "File size exceeds 30MB limit" in response.json()["detail"]

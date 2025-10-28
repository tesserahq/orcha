from uuid import uuid4


def test_list_sources(client):
    """Test GET /sources endpoint."""
    response = client.get("/sources")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_create_source(client):
    """Test POST /sources endpoint."""
    response = client.post(
        "/sources",
        json={
            "name": "Test Source",
            "description": "Test description",
            "identifier": "test-source-001",
        },
    )
    assert response.status_code == 201
    source = response.json()
    assert source["name"] == "Test Source"
    assert source["description"] == "Test description"
    assert source["identifier"] == "test-source-001"
    assert "id" in source
    assert "created_at" in source
    assert "updated_at" in source


def test_get_source(client, test_source):
    """Test GET /sources/{id} endpoint."""
    response = client.get(f"/sources/{test_source.id}")
    assert response.status_code == 200
    source = response.json()
    assert source["id"] == str(test_source.id)
    assert source["name"] == test_source.name
    assert source["identifier"] == test_source.identifier


def test_get_source_not_found(client):
    """Test GET /sources/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.get(f"/sources/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Source not found"


def test_update_source(client, test_source):
    """Test PUT /sources/{id} endpoint."""
    update_data = {
        "name": "Updated Source Name",
        "description": "Updated description",
    }
    response = client.put(
        f"/sources/{test_source.id}",
        json=update_data,
    )
    assert response.status_code == 200
    source = response.json()
    assert source["name"] == update_data["name"]
    assert source["description"] == update_data["description"]
    # identifier should remain unchanged
    assert source["identifier"] == test_source.identifier


def test_update_source_not_found(client):
    """Test PUT /sources/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.put(
        f"/sources/{non_existent_id}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Source not found"


def test_delete_source(client, test_source):
    """Test DELETE /sources/{id} endpoint."""
    source_id = test_source.id
    response = client.delete(f"/sources/{source_id}")
    assert response.status_code == 204

    # Verify it's soft deleted (should not appear in list)
    response = client.get(f"/sources/{source_id}")
    assert response.status_code == 404


def test_delete_source_not_found(client):
    """Test DELETE /sources/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.delete(f"/sources/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Source not found"


def test_create_source_duplicate_identifier(client):
    """Test creating a source with duplicate identifier."""
    # Create first source
    response = client.post(
        "/sources",
        json={
            "name": "First Source",
            "description": "First description",
            "identifier": "unique-identifier",
        },
    )
    assert response.status_code == 201

    # Try to create another with same identifier
    response = client.post(
        "/sources",
        json={
            "name": "Second Source",
            "description": "Second description",
            "identifier": "unique-identifier",
        },
    )
    assert response.status_code == 400
    assert "identifier already exists" in response.json()["detail"].lower()


def test_update_source_duplicate_identifier(client):
    """Test updating a source to use an existing identifier."""
    # Create two sources
    response1 = client.post(
        "/sources",
        json={
            "name": "Source 1",
            "description": "Description 1",
            "identifier": "identifier-1",
        },
    )
    assert response1.status_code == 201
    source1_id = response1.json()["id"]

    response2 = client.post(
        "/sources",
        json={
            "name": "Source 2",
            "description": "Description 2",
            "identifier": "identifier-2",
        },
    )
    assert response2.status_code == 201

    # Try to update source2 to use source1's identifier
    response = client.put(
        f"/sources/{source1_id}",
        json={"identifier": "identifier-2"},
    )
    assert response.status_code == 400
    assert "identifier already exists" in response.json()["detail"].lower()


def test_create_source_minimal_data(client):
    """Test creating a source with only required fields."""
    response = client.post(
        "/sources",
        json={
            "name": "Minimal Source",
            "identifier": "minimal-001",
        },
    )
    assert response.status_code == 201
    source = response.json()
    assert source["name"] == "Minimal Source"
    assert source["identifier"] == "minimal-001"
    assert source["description"] is None


def test_list_sources_pagination(client, test_source):
    """Test pagination in GET /sources endpoint."""
    # Create another source
    client.post(
        "/sources",
        json={
            "name": "Another Source",
            "description": "Another description",
            "identifier": "another-001",
        },
    )

    # Test with pagination
    response = client.get("/sources?page=1&size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1

    response = client.get("/sources?page=2&size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1

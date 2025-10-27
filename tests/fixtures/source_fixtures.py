import pytest
from app.models.source import Source


@pytest.fixture(scope="function")
def test_source(db, faker):
    """Create a test source for use in tests."""
    source_data = {
        "name": faker.company(),
        "description": faker.text(max_nb_chars=200),
        "identifier": faker.slug(),
    }

    source = Source(**source_data)
    db.add(source)
    db.commit()
    db.refresh(source)

    return source


@pytest.fixture(scope="function")
def setup_source(db, faker):
    """Create a test source for use in tests."""
    source_data = {
        "name": faker.company(),
        "description": faker.text(max_nb_chars=200),
        "identifier": faker.slug(),
    }

    source = Source(**source_data)
    db.add(source)
    db.commit()
    db.refresh(source)

    return source


@pytest.fixture(scope="function")
def setup_another_source(db, faker):
    """Create another test source for use in tests."""
    source_data = {
        "name": faker.company(),
        "description": faker.text(max_nb_chars=200),
        "identifier": faker.slug(),
    }

    source = Source(**source_data)
    db.add(source)
    db.commit()
    db.refresh(source)

    return source

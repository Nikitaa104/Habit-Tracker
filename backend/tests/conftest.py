import pytest
from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Roll back after every test to keep tests isolated."""
    with app.app_context():
        yield
        _db.session.rollback()
        # Truncate all tables
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()

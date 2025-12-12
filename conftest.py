#!/usr/bin/env python3
"""
pytest configuration and shared fixtures for manage_books tests.

This file provides shared test configuration and fixtures that can be
used across all test files in the test suite.
"""

import sys
from pathlib import Path

import pytest

# Add the project directory to sys.path for imports
project_dir = Path(__file__).parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# ============================================================================
# SESSION-SCOPED FIXTURES
# ============================================================================


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory path."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a session-scoped temporary directory for test data."""
    return tmp_path_factory.mktemp("test_data")


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================


@pytest.fixture
def simple_book_dict():
    """Return a simple book dictionary for testing."""
    return {
        "author": "John Smith",
        "book_category": "Music",
        "book_size": "A4",
        "language": "fra",
        "page_count": 150,
        "price": 12.50,
        "title": "Music Theory Basics",
    }


@pytest.fixture
def multi_part_book_dict():
    """Return a multi-part book dictionary for testing."""
    return {
        "author": "Jane Doe",
        "title": "Complete Works",
        "data": [
            {
                "author": "Jane Doe",
                "book_category": "Philosophy",
                "book_size": "A5",
                "language": "eng",
                "page_count": 200,
                "price": 15.00,
                "title": "Volume 1",
            },
            {
                "author": "Jane Doe",
                "book_category": "Philosophy",
                "book_size": "A5",
                "language": "eng",
                "page_count": 220,
                "price": 16.00,
                "title": "Volume 2",
            },
        ],
    }


@pytest.fixture
def complex_nested_book():
    """Return a complex nested book structure for testing."""
    return {
        "author": "Complex Author",
        "title": "Main Series",
        "data": [
            {
                "author": "Complex Author",
                "title": "Sub-Series 1",
                "data": [
                    {
                        "author": "Complex Author",
                        "book_category": "History",
                        "book_size": "Digest",
                        "language": "lat",
                        "page_count": 300,
                        "price": 20.00,
                        "title": "Part 1",
                    },
                    {
                        "author": "Complex Author",
                        "book_category": "History",
                        "book_size": "Digest",
                        "language": "lat",
                        "page_count": 350,
                        "price": 22.00,
                        "title": "Part 2",
                    },
                ],
            },
        ],
    }


# ============================================================================
# HELPER FIXTURES
# ============================================================================


@pytest.fixture
def mock_subprocess_success():
    """Return a mock subprocess result for successful operations."""
    from unittest.mock import Mock

    result = Mock()
    result.returncode = 0
    result.stdout = "Success"
    result.stderr = ""
    return result


@pytest.fixture
def mock_subprocess_failure():
    """Return a mock subprocess result for failed operations."""
    from unittest.mock import Mock

    result = Mock()
    result.returncode = 1
    result.stdout = ""
    result.stderr = "Error occurred"
    return result


# ============================================================================
# AUTO-USE FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment between tests to ensure isolation."""
    # This runs before each test
    yield
    # Cleanup after each test if needed
    pass


# ============================================================================
# CUSTOM ASSERTIONS
# ============================================================================


def assert_valid_book_structure(book_dict):
    """
    Assert that a book dictionary has the correct structure.

    Args:
        book_dict: Dictionary representing a book

    Raises:
        AssertionError: If book structure is invalid
    """
    assert isinstance(book_dict, dict), "Book must be a dictionary"
    assert "author" in book_dict, "Book must have 'author' field"
    assert "title" in book_dict, "Book must have 'title' field"

    # Check if it's a simple book or multi-part book
    if "data" in book_dict:
        # Multi-part book
        assert isinstance(book_dict["data"], list), "Book 'data' must be a list"
        assert len(book_dict["data"]) > 0, "Multi-part book must have at least one part"
    else:
        # Simple book - must have all required fields
        required_fields = ["author", "book_category", "book_size", "language", "page_count", "price", "title"]
        for field in required_fields:
            assert field in book_dict, f"Simple book must have '{field}' field"

        # Validate types
        assert isinstance(book_dict["page_count"], int), "page_count must be an integer"
        assert isinstance(book_dict["price"], (int, float)), "price must be numeric"
        assert book_dict["page_count"] > 0, "page_count must be positive"
        assert book_dict["price"] >= 0, "price must be non-negative"


# Make custom assertions available to tests
pytest.assert_valid_book_structure = assert_valid_book_structure

#!/usr/bin/env python3
"""
Comprehensive pytest unit tests for manage_books.py

Tests cover:
- BookManager: JSON file operations, book display, and search
- BookCreator: Creating simple and multi-part books
- BookEditor: Editing existing books and adding parts
- UserInterface: Input validation and user interactions
- GitManager: Git operations (add, commit, push)
- gen_table execution and error handling
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest
import re

# Import the module to test
import manage_books
from manage_books import (
    BOOK_CATEGORIES,
    BOOK_SIZES,
    LANGUAGES,
    BookCreator,
    BookEditor,
    BookManager,
    GitManager,
    UserInterface,
    run_gen_table,
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_books_data():
    """Sample book data for testing."""
    return [
        {
            "author": "Test Author",
            "book_category": "Music",
            "book_size": "A4",
            "language": "fra",
            "page_count": 100,
            "price": 10.50,
            "title": "Simple Book",
        },
        {
            "author": "Multi Author",
            "title": "Multi-Part Book",
            "data": [
                {
                    "author": "Multi Author",
                    "book_category": "Philosophy",
                    "book_size": "A5",
                    "language": "eng",
                    "page_count": 200,
                    "price": 15.00,
                    "title": "Part 1",
                },
                {
                    "author": "Multi Author",
                    "book_category": "Philosophy",
                    "book_size": "A5",
                    "language": "eng",
                    "page_count": 250,
                    "price": 17.50,
                    "title": "Part 2",
                },
            ],
        },
    ]


@pytest.fixture
def temp_data_file(tmp_path, sample_books_data):
    """Create a temporary data file for testing."""
    data_file = tmp_path / "data.txt"
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(sample_books_data, f, indent=4, ensure_ascii=False)
    return data_file


@pytest.fixture
def book_manager(temp_data_file):
    """Create a BookManager instance with temp data file."""
    return BookManager(data_file=temp_data_file)


@pytest.fixture
def user_interface():
    """Create a UserInterface instance."""
    return UserInterface()


@pytest.fixture
def book_creator(user_interface):
    """Create a BookCreator instance."""
    return BookCreator(ui=user_interface)


@pytest.fixture
def book_editor(book_manager, user_interface):
    """Create a BookEditor instance."""
    return BookEditor(manager=book_manager, ui=user_interface)


@pytest.fixture
def git_manager(tmp_path):
    """Create a GitManager instance with temp repo path."""
    return GitManager(repo_path=tmp_path)


# ============================================================================
# BOOKMANAGER TESTS
# ============================================================================


class TestBookManager:
    """Test suite for BookManager class."""

    def test_load_books_success(self, temp_data_file, sample_books_data, capsys):
        """Test successful loading of books from JSON file."""
        manager = BookManager(data_file=temp_data_file)

        assert len(manager.books) == 2
        assert manager.books == sample_books_data

        captured = capsys.readouterr()
        assert "Loaded 2 book entries" in captured.out

    def test_load_books_file_not_found(self, tmp_path):
        """Test loading books when file doesn't exist."""
        non_existent_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SystemExit) as exc_info:
            BookManager(data_file=non_existent_file)

        assert exc_info.value.code == 1

    def test_load_books_invalid_json(self, tmp_path):
        """Test loading books with invalid JSON content."""
        invalid_json_file = tmp_path / "invalid.txt"
        with open(invalid_json_file, "w") as f:
            f.write("{invalid json content")

        with pytest.raises(SystemExit) as exc_info:
            BookManager(data_file=invalid_json_file)

        assert exc_info.value.code == 1

    def test_save_books_success(self, book_manager, temp_data_file, capsys):
        """Test successful saving of books to JSON file."""
        # Add a new book
        book_manager.books.append(
            {
                "author": "New Author",
                "book_category": "History",
                "book_size": "Digest",
                "language": "fra",
                "page_count": 300,
                "price": 20.00,
                "title": "New Book",
            }
        )

        book_manager.save_books()

        # Verify file was updated
        with open(temp_data_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        assert len(saved_data) == 3
        assert saved_data[2]["title"] == "New Book"

        captured = capsys.readouterr()
        assert "Data saved successfully" in captured.out

    def test_save_books_error(self, book_manager):
        """Test save_books handles write errors gracefully."""
        # Make the file path invalid
        book_manager.data_file = Path("/invalid/path/data.txt")

        with pytest.raises(SystemExit) as exc_info:
            book_manager.save_books()

        assert exc_info.value.code == 1

    def test_display_books_simple(self, book_manager, capsys):
        """Test displaying simple books."""
        book_manager.display_books()

        captured = capsys.readouterr()
        output = strip_ansi_codes(captured.out)
        assert "1. Simple Book - Test Author" in output
        assert "2. Multi-Part Book - Multi Author" in output

    def test_display_books_with_nested_data(self, book_manager, capsys):
        """Test displaying books with nested data."""
        book_manager.display_books()

        captured = capsys.readouterr()
        output = strip_ansi_codes(captured.out)
        # Check that nested books are indented
        assert "  1. Part 1 - Multi Author" in output
        assert "  2. Part 2 - Multi Author" in output

    def test_find_book_by_index_simple_book(self, book_manager):
        """Test finding a simple book by index."""
        book, _ = book_manager.find_book_by_index(book_manager.books, 1)

        assert book is not None
        assert book["title"] == "Simple Book"
        assert book["author"] == "Test Author"

    def test_find_book_by_index_nested_book(self, book_manager):
        """Test finding a nested book by index."""
        book, _ = book_manager.find_book_by_index(book_manager.books, 3)

        assert book is not None
        assert book["title"] == "Part 1"

    def test_find_book_by_index_not_found(self, book_manager):
        """Test finding a book with invalid index."""
        book, _ = book_manager.find_book_by_index(book_manager.books, 100)

        assert book is None

    def test_find_book_by_index_boundary(self, book_manager):
        """Test finding book at boundary indices."""
        # First book
        book, _ = book_manager.find_book_by_index(book_manager.books, 1)
        assert book["title"] == "Simple Book"

        # Last nested book
        book, _ = book_manager.find_book_by_index(book_manager.books, 4)
        assert book["title"] == "Part 2"


# ============================================================================
# USERINTERFACE TESTS
# ============================================================================


class TestUserInterface:
    """Test suite for UserInterface class."""

    def test_get_int_input_valid(self, user_interface):
        """Test getting valid integer input."""
        with patch("builtins.input", return_value="42"):
            result = user_interface.get_int_input("Enter number: ")
            assert result == 42

    def test_get_int_input_minimum_value(self, user_interface):
        """Test integer input with minimum value validation."""
        with patch("builtins.input", side_effect=["0", "5", "10"]):
            result = user_interface.get_int_input("Enter number: ", min_value=10)
            assert result == 10

    def test_get_int_input_invalid_then_valid(self, user_interface, capsys):
        """Test integer input with invalid input followed by valid."""
        with patch("builtins.input", side_effect=["invalid", "abc", "42"]):
            result = user_interface.get_int_input("Enter number: ")
            assert result == 42

            captured = capsys.readouterr()
            assert "Invalid input" in captured.out

    def test_get_int_input_keyboard_interrupt(self, user_interface):
        """Test integer input handles keyboard interrupt."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as exc_info:
                user_interface.get_int_input("Enter number: ")
            assert exc_info.value.code == 0

    def test_get_float_input_valid(self, user_interface):
        """Test getting valid float input."""
        with patch("builtins.input", return_value="19.99"):
            result = user_interface.get_float_input("Enter price: ")
            assert result == 19.99

    def test_get_float_input_minimum_value(self, user_interface):
        """Test float input with minimum value validation."""
        with patch("builtins.input", side_effect=["-5.0", "0.0", "10.5"]):
            result = user_interface.get_float_input("Enter price: ", min_value=10.0)
            assert result == 10.5

    def test_get_float_input_invalid_then_valid(self, user_interface, capsys):
        """Test float input with invalid input followed by valid."""
        with patch("builtins.input", side_effect=["invalid", "12.34"]):
            result = user_interface.get_float_input("Enter price: ")
            assert result == 12.34

            captured = capsys.readouterr()
            assert "Invalid input" in captured.out

    def test_get_float_input_keyboard_interrupt(self, user_interface):
        """Test float input handles keyboard interrupt."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                user_interface.get_float_input("Enter price: ")

    def test_get_choice_input_by_number(self, user_interface):
        """Test getting choice input by number."""
        choices = ["Option A", "Option B", "Option C"]
        with patch("builtins.input", return_value="2"):
            result = user_interface.get_choice_input("Choose: ", choices)
            assert result == "Option B"

    def test_get_choice_input_by_text(self, user_interface):
        """Test getting choice input by exact text."""
        choices = ["Music", "Philosophy", "History"]
        with patch("builtins.input", return_value="Philosophy"):
            result = user_interface.get_choice_input("Choose: ", choices)
            assert result == "Philosophy"

    def test_get_choice_input_invalid_then_valid(self, user_interface, capsys):
        """Test choice input with invalid choice followed by valid."""
        choices = ["A", "B", "C"]
        with patch("builtins.input", side_effect=["99", "invalid", "1"]):
            result = user_interface.get_choice_input("Choose: ", choices)
            assert result == "A"

            captured = capsys.readouterr()
            assert "Invalid choice" in captured.out or "Please enter a number" in captured.out

    def test_get_choice_input_keyboard_interrupt(self, user_interface):
        """Test choice input handles keyboard interrupt."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                user_interface.get_choice_input("Choose: ", ["A", "B"])

    def test_get_text_input_valid(self, user_interface):
        """Test getting valid text input."""
        with patch("builtins.input", return_value="Test Title"):
            result = user_interface.get_text_input("Enter title: ")
            assert result == "Test Title"

    def test_get_text_input_strips_whitespace(self, user_interface):
        """Test that text input strips leading/trailing whitespace."""
        with patch("builtins.input", return_value="  Spaced Text  "):
            result = user_interface.get_text_input("Enter text: ")
            assert result == "Spaced Text"

    def test_get_text_input_empty_not_allowed(self, user_interface, capsys):
        """Test text input rejects empty input when not allowed."""
        with patch("builtins.input", side_effect=["", "   ", "Valid"]):
            result = user_interface.get_text_input("Enter text: ", allow_empty=False)
            assert result == "Valid"

            captured = capsys.readouterr()
            assert "cannot be empty" in captured.out

    def test_get_text_input_empty_allowed(self, user_interface):
        """Test text input allows empty input when configured."""
        with patch("builtins.input", return_value=""):
            result = user_interface.get_text_input("Enter text: ", allow_empty=True)
            assert result == ""

    def test_get_text_input_keyboard_interrupt(self, user_interface):
        """Test text input handles keyboard interrupt."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                user_interface.get_text_input("Enter text: ")

    def test_confirm_yes_variations(self, user_interface):
        """Test confirm accepts various yes responses."""
        for response in ["y", "yes", "Y", "YES"]:
            with patch("builtins.input", return_value=response):
                assert user_interface.confirm("Continue?") is True

    def test_confirm_no_variations(self, user_interface):
        """Test confirm accepts various no responses."""
        for response in ["n", "no", "N", "NO"]:
            with patch("builtins.input", return_value=response):
                assert user_interface.confirm("Continue?") is False

    def test_confirm_invalid_then_valid(self, user_interface, capsys):
        """Test confirm handles invalid input followed by valid."""
        with patch("builtins.input", side_effect=["maybe", "sure", "y"]):
            result = user_interface.confirm("Continue?")
            assert result is True

            captured = capsys.readouterr()
            assert "Please enter 'y' or 'n'" in captured.out

    def test_confirm_keyboard_interrupt(self, user_interface):
        """Test confirm handles keyboard interrupt."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                user_interface.confirm("Continue?")


# ============================================================================
# BOOKCREATOR TESTS
# ============================================================================


class TestBookCreator:
    """Test suite for BookCreator class."""

    def test_create_simple_book_with_params(self, book_creator):
        """Test creating a simple book with all parameters provided."""
        book = book_creator.create_simple_book(
            author="John Doe",
            book_category="Music",
            book_size="A4",
            language="eng",
            title="Test Book",
            page_count=150,
            price=12.99,
        )

        assert book["author"] == "John Doe"
        assert book["book_category"] == "Music"
        assert book["book_size"] == "A4"
        assert book["language"] == "eng"
        assert book["title"] == "Test Book"
        assert book["page_count"] == 150
        assert book["price"] == 12.99
        assert "data" not in book

    def test_create_simple_book_with_prompts(self, book_creator):
        """Test creating a simple book with user input prompts."""
        with patch.object(
            book_creator.ui, "get_int_input", return_value=200
        ), patch.object(book_creator.ui, "get_float_input", return_value=15.50):
            book = book_creator.create_simple_book(
                author="Jane Smith",
                book_category="Philosophy",
                book_size="A5",
                language="fra",
                title="Philosophy Book",
            )

            assert book["page_count"] == 200
            assert book["price"] == 15.50

    def test_create_simple_book_validates_types(self, book_creator):
        """Test that simple book validates data types."""
        book = book_creator.create_simple_book(
            author="Author",
            book_category="Music",
            book_size="A4",
            language="eng",
            title="Title",
            page_count=100,
            price=10.5,
        )

        assert isinstance(book["page_count"], int)
        assert isinstance(book["price"], float)

    def test_create_multi_part_book(self, book_creator, capsys):
        """Test creating a multi-part book."""
        with patch.object(
            book_creator.ui, "get_text_input", side_effect=["Part 1", "Part 2"]
        ), patch.object(
            book_creator.ui, "get_int_input", side_effect=[100, 150]
        ), patch.object(
            book_creator.ui, "get_float_input", side_effect=[10.00, 12.50]
        ):
            book = book_creator.create_multi_part_book(
                author="Series Author",
                book_category="History",
                book_size="Digest",
                language="lat",
                main_title="History Series",
                num_parts=2,
            )

            assert book["author"] == "Series Author"
            assert book["title"] == "History Series"
            assert "data" in book
            assert len(book["data"]) == 2

            # Check first part
            assert book["data"][0]["title"] == "Part 1"
            assert book["data"][0]["page_count"] == 100
            assert book["data"][0]["price"] == 10.00
            assert book["data"][0]["author"] == "Series Author"

            # Check second part
            assert book["data"][1]["title"] == "Part 2"
            assert book["data"][1]["page_count"] == 150
            assert book["data"][1]["price"] == 12.50

    def test_create_multi_part_book_single_part(self, book_creator):
        """Test creating a multi-part book with single part."""
        with patch.object(
            book_creator.ui, "get_text_input", return_value="Only Part"
        ), patch.object(
            book_creator.ui, "get_int_input", return_value=100
        ), patch.object(
            book_creator.ui, "get_float_input", return_value=10.00
        ):
            book = book_creator.create_multi_part_book(
                author="Author",
                book_category="Music",
                book_size="A4",
                language="fra",
                main_title="Single",
                num_parts=1,
            )

            assert len(book["data"]) == 1

    def test_add_new_book_single_part_accepted(self, book_creator, capsys):
        """Test adding a new single-part book with confirmation."""
        with patch.object(
            book_creator.ui, "get_int_input", return_value=1
        ), patch.object(
            book_creator.ui, "get_text_input", side_effect=["Author", "Title"]
        ), patch.object(
            book_creator.ui, "get_choice_input", side_effect=["Music", "A4", "fra"]
        ), patch.object(
            book_creator.ui, "get_float_input", return_value=10.00
        ), patch.object(
            book_creator.ui, "confirm", return_value=True
        ):
            book = book_creator.add_new_book()

            assert book is not None
            assert book["title"] == "Title"
            assert book["author"] == "Author"

    def test_add_new_book_rejected(self, book_creator, capsys):
        """Test adding a new book but rejecting at confirmation."""
        with patch.object(
            book_creator.ui, "get_int_input", return_value=1
        ), patch.object(
            book_creator.ui, "get_text_input", side_effect=["Author", "Title"]
        ), patch.object(
            book_creator.ui, "get_choice_input", side_effect=["Music", "A4", "fra"]
        ), patch.object(
            book_creator.ui, "get_float_input", return_value=10.00
        ), patch.object(
            book_creator.ui, "confirm", return_value=False
        ):
            book = book_creator.add_new_book()

            assert book is None

            captured = capsys.readouterr()
            assert "Book not added" in captured.out

    def test_add_new_book_multi_part(self, book_creator):
        """Test adding a new multi-part book."""
        with patch.object(
            book_creator.ui, "get_int_input", side_effect=[2, 100, 150]
        ), patch.object(
            book_creator.ui,
            "get_text_input",
            side_effect=["Author", "Main Title", "Part 1", "Part 2"],
        ), patch.object(
            book_creator.ui, "get_choice_input", side_effect=["Music", "A4", "fra"]
        ), patch.object(
            book_creator.ui, "get_float_input", side_effect=[10.00, 12.00]
        ), patch.object(
            book_creator.ui, "confirm", return_value=True
        ):
            book = book_creator.add_new_book()

            assert book is not None
            assert "data" in book
            assert len(book["data"]) == 2


# ============================================================================
# BOOKEDITOR TESTS
# ============================================================================


class TestBookEditor:
    """Test suite for BookEditor class."""

    def test_edit_simple_book_author(self, book_editor, book_manager):
        """Test editing author of a simple book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[1, 1]
        ), patch.object(
            book_editor.ui, "get_text_input", return_value="New Author"
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[0]["author"] == "New Author"

    def test_edit_simple_book_title(self, book_editor, book_manager):
        """Test editing title of a simple book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[1, 2]
        ), patch.object(
            book_editor.ui, "get_text_input", return_value="New Title"
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[0]["title"] == "New Title"

    def test_edit_simple_book_page_count(self, book_editor, book_manager):
        """Test editing page count of a simple book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[1, 6, 500]
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[0]["page_count"] == 500

    def test_edit_simple_book_price(self, book_editor, book_manager):
        """Test editing price of a simple book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[1, 7]
        ), patch.object(
            book_editor.ui, "get_float_input", return_value=25.99
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[0]["price"] == 25.99

    def test_edit_simple_book_category(self, book_editor, book_manager):
        """Test editing category of a simple book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[1, 3]
        ), patch.object(
            book_editor.ui, "get_choice_input", return_value="Philosophy"
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[0]["book_category"] == "Philosophy"

    def test_edit_simple_book_size(self, book_editor, book_manager):
        """Test editing size of a simple book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[1, 4]
        ), patch.object(
            book_editor.ui, "get_choice_input", return_value="A5"
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[0]["book_size"] == "A5"

    def test_edit_simple_book_language(self, book_editor, book_manager):
        """Test editing language of a simple book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[1, 5]
        ), patch.object(
            book_editor.ui, "get_choice_input", return_value="lat"
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[0]["language"] == "lat"

    def test_edit_simple_book_cancel(self, book_editor):
        """Test canceling edit of a simple book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[1, 0]
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is False

    def test_edit_book_invalid_selection(self, book_editor, capsys):
        """Test editing with invalid book selection."""
        with patch.object(
            book_editor.ui, "get_int_input", return_value=999
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is False
            captured = capsys.readouterr()
            assert "Invalid selection" in captured.out

    def test_edit_book_cancel_selection(self, book_editor, capsys):
        """Test canceling book selection."""
        with patch.object(
            book_editor.ui, "get_int_input", return_value=0
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is False
            captured = capsys.readouterr()
            assert "Edit cancelled" in captured.out

    def test_edit_multi_part_book_main_title(self, book_editor, book_manager):
        """Test editing main title of a multi-part book."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[2, 2]
        ), patch.object(
            book_editor.ui, "get_text_input", return_value="New Main Title"
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[1]["title"] == "New Main Title"

    def test_edit_multi_part_book_author(self, book_editor, book_manager):
        """Test editing author of a multi-part book updates all parts."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[2, 3]
        ), patch.object(
            book_editor.ui, "get_text_input", return_value="Updated Author"
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert book_manager.books[1]["author"] == "Updated Author"
            # Check all parts have updated author
            for part in book_manager.books[1]["data"]:
                assert part["author"] == "Updated Author"

    def test_add_part_to_book_use_existing_values(self, book_editor, book_manager):
        """Test adding a part to a multi-part book using existing values."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[2, 1, 300]
        ), patch.object(
            book_editor.ui, "get_text_input", return_value="Part 3"
        ), patch.object(
            book_editor.ui, "get_float_input", return_value=20.00
        ), patch.object(
            book_editor.ui, "confirm", return_value=True
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert len(book_manager.books[1]["data"]) == 3
            assert book_manager.books[1]["data"][2]["title"] == "Part 3"
            assert book_manager.books[1]["data"][2]["page_count"] == 300
            assert book_manager.books[1]["data"][2]["price"] == 20.00

    def test_add_part_to_book_new_values(self, book_editor, book_manager):
        """Test adding a part to a multi-part book with new values."""
        with patch.object(
            book_editor.ui, "get_int_input", side_effect=[2, 1, 250]
        ), patch.object(
            book_editor.ui, "get_text_input", return_value="Part 3"
        ), patch.object(
            book_editor.ui, "get_float_input", return_value=18.00
        ), patch.object(
            book_editor.ui, "confirm", return_value=False
        ), patch.object(
            book_editor.ui,
            "get_choice_input",
            side_effect=["History", "Digest", "lat"],
        ), patch.object(
            book_editor.manager, "display_books"
        ):
            result = book_editor.edit_book()

            assert result is True
            assert len(book_manager.books[1]["data"]) == 3
            new_part = book_manager.books[1]["data"][2]
            assert new_part["book_category"] == "History"
            assert new_part["book_size"] == "Digest"
            assert new_part["language"] == "lat"

    def test_get_first_leaf_book(self, book_editor, book_manager):
        """Test getting the first leaf book from nested structure."""
        leaf = book_editor._get_first_leaf_book(book_manager.books[1]["data"])

        assert leaf is not None
        assert leaf["title"] == "Part 1"

    def test_get_first_leaf_book_empty(self, book_editor):
        """Test getting first leaf book from empty list."""
        leaf = book_editor._get_first_leaf_book([])
        assert leaf is None

    def test_update_author_recursively(self, book_editor):
        """Test recursive author update in nested structure."""
        nested_data = [
            {"author": "Old", "title": "Book 1"},
            {
                "author": "Old",
                "title": "Parent",
                "data": [
                    {"author": "Old", "title": "Child 1"},
                    {"author": "Old", "title": "Child 2"},
                ],
            },
        ]

        book_editor._update_author_recursively(nested_data, "New Author")

        assert nested_data[0]["author"] == "New Author"
        assert nested_data[1]["author"] == "New Author"
        assert nested_data[1]["data"][0]["author"] == "New Author"
        assert nested_data[1]["data"][1]["author"] == "New Author"


# ============================================================================
# GITMANAGER TESTS
# ============================================================================


class TestGitManager:
    """Test suite for GitManager class."""

    def test_run_command_success(self, git_manager):
        """Test running a successful git command."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            exit_code, stdout, stderr = git_manager.run_command(["git", "status"])

            assert exit_code == 0
            assert stdout == "Success output"
            assert stderr == ""

    def test_run_command_failure(self, git_manager):
        """Test running a failed git command."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error message"

        with patch("subprocess.run", return_value=mock_result):
            exit_code, stdout, stderr = git_manager.run_command(["git", "add", "file"])

            assert exit_code == 1
            assert stderr == "Error message"

    def test_run_command_timeout(self, git_manager):
        """Test git command timeout handling."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 30)):
            exit_code, stdout, stderr = git_manager.run_command(["git", "push"])

            assert exit_code == -1
            assert "timed out" in stderr

    def test_run_command_exception(self, git_manager):
        """Test git command exception handling."""
        with patch("subprocess.run", side_effect=Exception("Unknown error")):
            exit_code, stdout, stderr = git_manager.run_command(["git", "commit"])

            assert exit_code == -1
            assert "Unknown error" in stderr

    def test_commit_and_push_success(self, git_manager, capsys):
        """Test successful git commit and push."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = git_manager.commit_and_push("Test commit message")

            assert result is True

            captured = capsys.readouterr()
            assert "File staged successfully" in captured.out
            assert "Commit successful" in captured.out
            assert "Push successful" in captured.out

    def test_commit_and_push_stage_failure(self, git_manager, capsys):
        """Test git commit and push fails at staging."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Staging failed"

        with patch("subprocess.run", return_value=mock_result):
            result = git_manager.commit_and_push("Test message")

            assert result is False

            captured = capsys.readouterr()
            assert "Error staging file" in captured.out

    def test_commit_and_push_commit_failure(self, git_manager, capsys):
        """Test git commit and push fails at commit."""
        def mock_run(command, **kwargs):
            mock_result = Mock()
            if "add" in command:
                mock_result.returncode = 0
            elif "commit" in command:
                mock_result.returncode = 1
                mock_result.stderr = "Commit failed"
            else:
                mock_result.returncode = 0
            mock_result.stdout = ""
            return mock_result

        with patch("subprocess.run", side_effect=mock_run):
            result = git_manager.commit_and_push("Test message")

            assert result is False

            captured = capsys.readouterr()
            assert "Error committing" in captured.out

    def test_commit_and_push_push_failure(self, git_manager, capsys):
        """Test git commit and push fails at push."""
        def mock_run(command, **kwargs):
            mock_result = Mock()
            if "push" in command:
                mock_result.returncode = 1
                mock_result.stderr = "Push failed"
            else:
                mock_result.returncode = 0
            mock_result.stdout = ""
            return mock_result

        with patch("subprocess.run", side_effect=mock_run):
            result = git_manager.commit_and_push("Test message")

            assert result is False

            captured = capsys.readouterr()
            assert "Error pushing" in captured.out

    def test_commit_and_push_uses_correct_repo_path(self, tmp_path):
        """Test that git commands use the correct repository path."""
        git_mgr = GitManager(repo_path=tmp_path)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            git_mgr.commit_and_push("Test")

            # Verify all calls used correct cwd
            for call_args in mock_run.call_args_list:
                assert call_args.kwargs["cwd"] == tmp_path


# ============================================================================
# RUN_GEN_TABLE TESTS
# ============================================================================


class TestRunGenTable:
    """Test suite for run_gen_table function."""

    def test_run_gen_table_success(self, tmp_path, capsys):
        """Test successful execution of gen_table.py."""
        script_path = tmp_path / "gen_table.py"
        script_path.write_text("print('Table generated')")

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Table generated successfully"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = run_gen_table(script_path)

            assert result is True

            captured = capsys.readouterr()
            assert "Table generated successfully" in captured.out

    def test_run_gen_table_failure(self, tmp_path, capsys):
        """Test failed execution of gen_table.py."""
        script_path = tmp_path / "gen_table.py"
        script_path.write_text("import sys; sys.exit(1)")

        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error in script"

        with patch("subprocess.run", return_value=mock_result):
            result = run_gen_table(script_path)

            assert result is False

            captured = capsys.readouterr()
            assert "Error generating table" in captured.out

    def test_run_gen_table_timeout(self, tmp_path, capsys):
        """Test gen_table.py execution timeout."""
        script_path = tmp_path / "gen_table.py"
        script_path.write_text("")

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 30)):
            result = run_gen_table(script_path)

            assert result is False

            captured = capsys.readouterr()
            assert "timed out" in captured.out

    def test_run_gen_table_exception(self, tmp_path, capsys):
        """Test gen_table.py execution with exception."""
        script_path = tmp_path / "gen_table.py"

        with patch("subprocess.run", side_effect=Exception("Script error")):
            result = run_gen_table(script_path)

            assert result is False

            captured = capsys.readouterr()
            assert "Error running gen_table.py" in captured.out

    def test_run_gen_table_uses_correct_interpreter(self, tmp_path):
        """Test that gen_table.py uses correct Python interpreter."""
        script_path = tmp_path / "gen_table.py"
        script_path.write_text("")

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            run_gen_table(script_path)

            # Verify first argument is the Python interpreter
            call_args = mock_run.call_args[0][0]
            assert call_args[0] == sys.executable

    def test_run_gen_table_uses_correct_working_directory(self, tmp_path):
        """Test that gen_table.py runs in correct working directory."""
        script_path = tmp_path / "gen_table.py"
        script_path.write_text("")

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            run_gen_table(script_path)

            # Verify cwd is script's parent directory
            assert mock_run.call_args.kwargs["cwd"] == tmp_path


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_create_and_save_simple_book(self, book_manager, book_creator):
        """Test creating a simple book and saving to file."""
        # Create a book
        book = book_creator.create_simple_book(
            author="Integration Author",
            book_category="Music",
            book_size="A4",
            language="eng",
            title="Integration Book",
            page_count=200,
            price=15.00,
        )

        # Add to manager
        book_manager.books.append(book)

        # Save
        book_manager.save_books()

        # Reload and verify
        book_manager.load_books()
        assert len(book_manager.books) == 3
        assert book_manager.books[2]["title"] == "Integration Book"

    def test_create_and_edit_book(self, book_manager, book_creator, book_editor):
        """Test creating a book and then editing it."""
        # Create a book
        initial_count = len(book_manager.books)
        book = book_creator.create_simple_book(
            author="Original Author",
            book_category="Philosophy",
            book_size="A5",
            language="fra",
            title="Original Title",
            page_count=100,
            price=10.00,
        )

        book_manager.books.append(book)
        assert len(book_manager.books) == initial_count + 1

        # Edit the book
        book_manager.books[-1]["author"] = "Updated Author"
        book_manager.books[-1]["price"] = 12.50

        assert book_manager.books[-1]["author"] == "Updated Author"
        assert book_manager.books[-1]["price"] == 12.50

    def test_multi_part_book_workflow(self, book_manager, book_creator):
        """Test complete workflow for multi-part book."""
        with patch.object(
            book_creator.ui, "get_text_input", side_effect=["Vol 1", "Vol 2", "Vol 3"]
        ), patch.object(
            book_creator.ui, "get_int_input", side_effect=[100, 150, 200]
        ), patch.object(
            book_creator.ui, "get_float_input", side_effect=[10.0, 12.0, 14.0]
        ):
            book = book_creator.create_multi_part_book(
                author="Series Author",
                book_category="History",
                book_size="Digest",
                language="eng",
                main_title="History Series",
                num_parts=3,
            )

            book_manager.books.append(book)
            book_manager.save_books()

            # Verify structure
            assert book_manager.books[-1]["title"] == "History Series"
            assert len(book_manager.books[-1]["data"]) == 3

            # Verify all parts have correct author
            for part in book_manager.books[-1]["data"]:
                assert part["author"] == "Series Author"

    def test_git_workflow_after_save(self, book_manager, git_manager):
        """Test git workflow after saving books."""
        # Modify book data
        book_manager.books[0]["price"] = 99.99
        book_manager.save_books()

        # Mock git operations
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = git_manager.commit_and_push("Update book prices")
            assert result is True


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


class TestParametrized:
    """Parametrized tests for comprehensive coverage."""

    @pytest.mark.parametrize(
        "category",
        BOOK_CATEGORIES,
    )
    def test_all_book_categories(self, book_creator, category):
        """Test creating books with all available categories."""
        book = book_creator.create_simple_book(
            author="Test",
            book_category=category,
            book_size="A4",
            language="fra",
            title="Test",
            page_count=100,
            price=10.0,
        )
        assert book["book_category"] == category

    @pytest.mark.parametrize(
        "size",
        BOOK_SIZES,
    )
    def test_all_book_sizes(self, book_creator, size):
        """Test creating books with all available sizes."""
        book = book_creator.create_simple_book(
            author="Test",
            book_category="Music",
            book_size=size,
            language="fra",
            title="Test",
            page_count=100,
            price=10.0,
        )
        assert book["book_size"] == size

    @pytest.mark.parametrize(
        "lang_code",
        list(LANGUAGES.keys()),
    )
    def test_all_languages(self, book_creator, lang_code):
        """Test creating books with all available languages."""
        book = book_creator.create_simple_book(
            author="Test",
            book_category="Music",
            book_size="A4",
            language=lang_code,
            title="Test",
            page_count=100,
            price=10.0,
        )
        assert book["language"] == lang_code

    @pytest.mark.parametrize(
        "page_count,expected",
        [
            (1, 1),
            (50, 50),
            (100, 100),
            (500, 500),
            (1000, 1000),
        ],
    )
    def test_various_page_counts(self, book_creator, page_count, expected):
        """Test creating books with various page counts."""
        book = book_creator.create_simple_book(
            author="Test",
            book_category="Music",
            book_size="A4",
            language="fra",
            title="Test",
            page_count=page_count,
            price=10.0,
        )
        assert book["page_count"] == expected

    @pytest.mark.parametrize(
        "price,expected",
        [
            (0.01, 0.01),
            (5.0, 5.0),
            (10.50, 10.50),
            (99.99, 99.99),
            (100.0, 100.0),
        ],
    )
    def test_various_prices(self, book_creator, price, expected):
        """Test creating books with various prices."""
        book = book_creator.create_simple_book(
            author="Test",
            book_category="Music",
            book_size="A4",
            language="fra",
            title="Test",
            page_count=100,
            price=price,
        )
        assert book["price"] == expected

    @pytest.mark.parametrize(
        "num_parts",
        [1, 2, 3, 5, 10],
    )
    def test_various_part_counts(self, book_creator, num_parts):
        """Test creating multi-part books with various part counts."""
        with patch.object(
            book_creator.ui, "get_text_input", side_effect=[f"Part {i}" for i in range(num_parts)]
        ), patch.object(
            book_creator.ui, "get_int_input", side_effect=[100] * num_parts
        ), patch.object(
            book_creator.ui, "get_float_input", side_effect=[10.0] * num_parts
        ):
            book = book_creator.create_multi_part_book(
                author="Test",
                book_category="Music",
                book_size="A4",
                language="fra",
                main_title="Test Series",
                num_parts=num_parts,
            )

            assert len(book["data"]) == num_parts


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_books_list(self, tmp_path):
        """Test BookManager with empty books list."""
        data_file = tmp_path / "empty.txt"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump([], f)

        manager = BookManager(data_file=data_file)
        assert len(manager.books) == 0

    def test_corrupted_json_structure(self, tmp_path):
        """Test BookManager with unexpected JSON structure."""
        data_file = tmp_path / "corrupted.txt"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump({"not": "a list"}, f)

        # Should load but might cause issues when trying to iterate
        manager = BookManager(data_file=data_file)
        # books should be the dict, which will cause issues later
        assert manager.books == {"not": "a list"}

    def test_special_characters_in_title(self, book_creator):
        """Test creating book with special characters in title."""
        book = book_creator.create_simple_book(
            author="Test Author",
            book_category="Music",
            book_size="A4",
            language="fra",
            title="Title with 'quotes' and \"double\" & special chars: é, à, ç",
            page_count=100,
            price=10.0,
        )

        assert "quotes" in book["title"]
        assert "&" in book["title"]

    def test_unicode_in_author_name(self, book_creator):
        """Test creating book with unicode characters in author."""
        book = book_creator.create_simple_book(
            author="Kœchlin über München",
            book_category="Music",
            book_size="A4",
            language="fra",
            title="Test",
            page_count=100,
            price=10.0,
        )

        assert book["author"] == "Kœchlin über München"

    def test_very_long_title(self, book_creator):
        """Test creating book with very long title."""
        long_title = "A" * 1000
        book = book_creator.create_simple_book(
            author="Test",
            book_category="Music",
            book_size="A4",
            language="fra",
            title=long_title,
            page_count=100,
            price=10.0,
        )

        assert len(book["title"]) == 1000

    def test_zero_price_edge_case(self, book_creator):
        """Test creating book with zero price."""
        # Note: UI validation requires >= 0.0, so 0.0 is valid
        book = book_creator.create_simple_book(
            author="Test",
            book_category="Music",
            book_size="A4",
            language="fra",
            title="Test",
            page_count=100,
            price=0.0,
        )

        assert book["price"] == 0.0

    def test_display_books_with_none_books(self, book_manager, capsys):
        """Test displaying books when books list is empty."""
        book_manager.books = []
        book_manager.display_books()

        captured = capsys.readouterr()
        # Should not crash, just produce no output
        assert captured.out == ""

    def test_find_book_by_index_zero(self, book_manager):
        """Test finding book with index 0."""
        book, _ = book_manager.find_book_by_index(book_manager.books, 0)
        assert book is None

    def test_find_book_by_index_negative(self, book_manager):
        """Test finding book with negative index."""
        book, _ = book_manager.find_book_by_index(book_manager.books, -1)
        assert book is None


# ============================================================================
# CONSTANTS TESTS
# ============================================================================


class TestConstants:
    """Test module constants are properly defined."""

    def test_book_categories_defined(self):
        """Test BOOK_CATEGORIES constant is defined correctly."""
        assert len(BOOK_CATEGORIES) == 5
        assert "Music" in BOOK_CATEGORIES
        assert "Religion & Spirituality" in BOOK_CATEGORIES
        assert "Philosophy" in BOOK_CATEGORIES
        assert "History" in BOOK_CATEGORIES
        assert "Education & languages" in BOOK_CATEGORIES

    def test_book_sizes_defined(self):
        """Test BOOK_SIZES constant is defined correctly."""
        assert len(BOOK_SIZES) == 7
        assert "A4" in BOOK_SIZES
        assert "A5" in BOOK_SIZES
        assert "Pocket" in BOOK_SIZES

    def test_languages_defined(self):
        """Test LANGUAGES constant is defined correctly."""
        assert len(LANGUAGES) == 4
        assert "fra" in LANGUAGES
        assert "lat" in LANGUAGES
        assert "eng" in LANGUAGES
        assert "heb" in LANGUAGES
        assert LANGUAGES["fra"] == "Français"
        assert LANGUAGES["lat"] == "Latin"
        assert LANGUAGES["eng"] == "Anglais"
        assert LANGUAGES["heb"] == "Hébreu"

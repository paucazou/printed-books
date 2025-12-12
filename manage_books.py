#!/usr/bin/env python3
"""
Book Management System for data.txt

This script provides an interactive CLI for managing books in the data.txt JSON file.
Supports adding new books (single or multi-part), editing existing books, and
automatic git commit/push after successful table generation.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# Type aliases for better code clarity
BookDict = Dict[str, Any]
BooksData = List[BookDict]


# Constants for book categories and sizes
BOOK_CATEGORIES = [
    "Music",
    "Religion & Spirituality",
    "Philosophy",
    "History",
]

BOOK_SIZES = [
    "Pocket",
    "Pocket Book",
    "Digest",
    "Executive",
    "US Trade",
    "A5",
    "A4",
]

LANGUAGES = {
    "fra": "Français",
    "lat": "Latin",
    "eng": "Anglais",
}


class BookManager:
    """Manages book data operations including loading, saving, and manipulation."""

    def __init__(self, data_file: Path = Path("/save/scripts/report_lulu/data.txt")):
        """Initialize the BookManager with a data file path."""
        self.data_file = data_file
        self.books: BooksData = []
        self.load_books()

    def load_books(self) -> None:
        """Load books from the JSON data file."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            print(f"Loaded {len(self.books)} book entries from {self.data_file}")
        except FileNotFoundError:
            print(f"Error: {self.data_file} not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {self.data_file}: {e}")
            sys.exit(1)

    def save_books(self) -> None:
        """Save books to the JSON data file with proper formatting."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.books, f, indent=4, ensure_ascii=False)
            print(f"\nData saved successfully to {self.data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
            sys.exit(1)

    def display_books(self, books: Optional[BooksData] = None, indent: int = 0) -> None:
        """Display books in a hierarchical format."""
        if books is None:
            books = self.books

        for idx, book in enumerate(books, 1):
            prefix = "  " * indent
            print(f"{prefix}{idx}. {book['title']} - {book['author']}")
            if "data" in book:
                self.display_books(book["data"], indent + 1)

    def find_book_by_index(
        self, books: BooksData, target_index: int, current_index: int = 0
    ) -> tuple[Optional[BookDict], int]:
        """
        Recursively find a book by its display index.
        Returns (book, new_current_index).
        """
        for book in books:
            current_index += 1
            if current_index == target_index:
                return book, current_index
            if "data" in book:
                found, current_index = self.find_book_by_index(
                    book["data"], target_index, current_index
                )
                if found is not None:
                    return found, current_index
        return None, current_index


class UserInterface:
    """Handles user interaction and input validation."""

    @staticmethod
    def get_int_input(prompt: str, min_value: int = 1) -> int:
        """Get and validate integer input from user."""
        while True:
            try:
                value = int(input(prompt))
                if value >= min_value:
                    return value
                print(f"Please enter a value >= {min_value}")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)

    @staticmethod
    def get_float_input(prompt: str, min_value: float = 0.0) -> float:
        """Get and validate float input from user."""
        while True:
            try:
                value = float(input(prompt))
                if value >= min_value:
                    return value
                print(f"Please enter a value >= {min_value}")
            except ValueError:
                print("Invalid input. Please enter a valid decimal number.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)

    @staticmethod
    def get_choice_input(
        prompt: str, choices: List[str], display_choices: bool = True
    ) -> str:
        """Get user choice from a list of options."""
        if display_choices:
            print("\nAvailable options:")
            for idx, choice in enumerate(choices, 1):
                print(f"  {idx}. {choice}")

        while True:
            try:
                choice_input = input(prompt)
                try:
                    choice_idx = int(choice_input)
                    if 1 <= choice_idx <= len(choices):
                        return choices[choice_idx - 1]
                    print(f"Please enter a number between 1 and {len(choices)}")
                except ValueError:
                    if choice_input in choices:
                        return choice_input
                    print(
                        "Invalid choice. Enter the number or exact text from the list."
                    )
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)

    @staticmethod
    def get_text_input(prompt: str, allow_empty: bool = False) -> str:
        """Get text input from user."""
        while True:
            try:
                value = input(prompt).strip()
                if value or allow_empty:
                    return value
                print("This field cannot be empty.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)

    @staticmethod
    def confirm(prompt: str) -> bool:
        """Get yes/no confirmation from user."""
        while True:
            try:
                response = input(f"{prompt} (y/n): ").strip().lower()
                if response in ["y", "yes"]:
                    return True
                elif response in ["n", "no"]:
                    return False
                print("Please enter 'y' or 'n'")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)


class BookCreator:
    """Handles creation of new book entries."""

    def __init__(self, ui: UserInterface):
        """Initialize BookCreator with a UserInterface instance."""
        self.ui = ui

    def create_simple_book(
        self,
        author: str,
        book_category: str,
        book_size: str,
        language: str,
        title: str,
        page_count: Optional[int] = None,
        price: Optional[float] = None,
    ) -> BookDict:
        """Create a simple book entry (no nested data)."""
        if page_count is None:
            page_count = self.ui.get_int_input("  Page count: ")
        if price is None:
            price = self.ui.get_float_input("  Price (€): ")

        return {
            "author": author,
            "book_category": book_category,
            "book_size": book_size,
            "language": language,
            "page_count": page_count,
            "price": price,
            "title": title,
        }

    def create_multi_part_book(
        self,
        author: str,
        book_category: str,
        book_size: str,
        language: str,
        main_title: str,
        num_parts: int,
    ) -> BookDict:
        """Create a multi-part book entry with nested data array."""
        parts: List[BookDict] = []

        print(f"\nEntering information for {num_parts} parts:")
        for i in range(1, num_parts + 1):
            print(f"\n--- Part {i}/{num_parts} ---")
            part_title = self.ui.get_text_input(f"  Title of part {i}: ")
            page_count = self.ui.get_int_input("  Page count: ")
            price = self.ui.get_float_input("  Price (€): ")

            part = self.create_simple_book(
                author=author,
                book_category=book_category,
                book_size=book_size,
                language=language,
                title=part_title,
                page_count=page_count,
                price=price,
            )
            parts.append(part)

        return {"author": author, "title": main_title, "data": parts}

    def add_new_book(self) -> Optional[BookDict]:
        """Interactive flow to add a new book."""
        print("\n" + "=" * 60)
        print("ADD NEW BOOK")
        print("=" * 60)

        # Get number of parts
        num_parts = self.ui.get_int_input(
            "\nHow many parts/volumes are in this book? (minimum 1): ", min_value=1
        )

        # Get common information
        print("\n--- Common Information ---")
        author = self.ui.get_text_input("Author: ")

        book_category = self.ui.get_choice_input(
            "Book category (enter number or text): ", BOOK_CATEGORIES
        )

        book_size = self.ui.get_choice_input(
            "Book size (enter number or text): ", BOOK_SIZES
        )

        language_code = self.ui.get_choice_input(
            "Language (enter number or code): ", list(LANGUAGES.keys())
        )

        if num_parts == 1:
            # Simple book
            title = self.ui.get_text_input("Title: ")
            book = self.create_simple_book(
                author=author,
                book_category=book_category,
                book_size=book_size,
                language=language_code,
                title=title,
            )
        else:
            # Multi-part book
            main_title = self.ui.get_text_input("Main title (collection/series name): ")
            book = self.create_multi_part_book(
                author=author,
                book_category=book_category,
                book_size=book_size,
                language=language_code,
                main_title=main_title,
                num_parts=num_parts,
            )

        # Show preview
        print("\n--- Preview ---")
        print(json.dumps(book, indent=2, ensure_ascii=False))

        if self.ui.confirm("\nAdd this book?"):
            return book
        else:
            print("Book not added.")
            return None


class BookEditor:
    """Handles editing of existing book entries."""

    def __init__(self, manager: BookManager, ui: UserInterface):
        """Initialize BookEditor with BookManager and UserInterface instances."""
        self.manager = manager
        self.ui = ui

    def edit_book(self) -> bool:
        """Interactive flow to edit an existing book."""
        print("\n" + "=" * 60)
        print("EDIT BOOK")
        print("=" * 60)

        print("\nCurrent books:")
        self.manager.display_books()

        choice = self.ui.get_int_input(
            "\nEnter the number of the book to edit (0 to cancel): ", min_value=0
        )

        if choice == 0:
            print("Edit cancelled.")
            return False

        book, _ = self.manager.find_book_by_index(self.manager.books, choice)

        if book is None:
            print("Invalid selection.")
            return False

        print(f"\nSelected: {book['title']} - {book['author']}")

        if "data" in book:
            return self._edit_multi_part_book(book)
        else:
            return self._edit_simple_book(book)

    def _edit_simple_book(self, book: BookDict) -> bool:
        """Edit a simple book entry."""
        print("\nWhat would you like to edit?")
        print("1. Author")
        print("2. Title")
        print("3. Book Category")
        print("4. Book Size")
        print("5. Language")
        print("6. Page Count")
        print("7. Price")
        print("0. Cancel")

        choice = self.ui.get_int_input("\nYour choice: ", min_value=0)

        if choice == 0:
            return False
        elif choice == 1:
            book["author"] = self.ui.get_text_input("New author: ")
        elif choice == 2:
            book["title"] = self.ui.get_text_input("New title: ")
        elif choice == 3:
            book["book_category"] = self.ui.get_choice_input(
                "New category: ", BOOK_CATEGORIES
            )
        elif choice == 4:
            book["book_size"] = self.ui.get_choice_input("New size: ", BOOK_SIZES)
        elif choice == 5:
            book["language"] = self.ui.get_choice_input(
                "New language: ", list(LANGUAGES.keys())
            )
        elif choice == 6:
            book["page_count"] = self.ui.get_int_input("New page count: ")
        elif choice == 7:
            book["price"] = self.ui.get_float_input("New price (€): ")
        else:
            print("Invalid choice.")
            return False

        print("Book updated successfully.")
        return True

    def _edit_multi_part_book(self, book: BookDict) -> bool:
        """Edit a multi-part book entry."""
        print("\nWhat would you like to do?")
        print("1. Add a new part/volume to this book")
        print("2. Edit main title")
        print("3. Edit author")
        print("0. Cancel")

        choice = self.ui.get_int_input("\nYour choice: ", min_value=0)

        if choice == 0:
            return False
        elif choice == 1:
            return self._add_part_to_book(book)
        elif choice == 2:
            book["title"] = self.ui.get_text_input("New main title: ")
            return True
        elif choice == 3:
            new_author = self.ui.get_text_input("New author: ")
            book["author"] = new_author
            # Update author in all nested parts
            self._update_author_recursively(book["data"], new_author)
            return True
        else:
            print("Invalid choice.")
            return False

    def _update_author_recursively(self, data: BooksData, new_author: str) -> None:
        """Recursively update author in all nested book entries."""
        for item in data:
            item["author"] = new_author
            if "data" in item:
                self._update_author_recursively(item["data"], new_author)

    def _add_part_to_book(self, book: BookDict) -> bool:
        """Add a new part to an existing multi-part book."""
        print(f"\nAdding new part to: {book['title']}")

        # Try to infer common fields from existing parts
        first_part = self._get_first_leaf_book(book["data"])
        if first_part:
            print("\nUsing common information from existing parts:")
            print(f"  Category: {first_part.get('book_category', 'N/A')}")
            print(f"  Size: {first_part.get('book_size', 'N/A')}")
            print(f"  Language: {first_part.get('language', 'N/A')}")

            use_existing = self.ui.confirm("Use these values for the new part?")
            if use_existing:
                book_category = first_part["book_category"]
                book_size = first_part["book_size"]
                language = first_part["language"]
            else:
                book_category = self.ui.get_choice_input(
                    "Book category: ", BOOK_CATEGORIES
                )
                book_size = self.ui.get_choice_input("Book size: ", BOOK_SIZES)
                language = self.ui.get_choice_input(
                    "Language: ", list(LANGUAGES.keys())
                )
        else:
            book_category = self.ui.get_choice_input("Book category: ", BOOK_CATEGORIES)
            book_size = self.ui.get_choice_input("Book size: ", BOOK_SIZES)
            language = self.ui.get_choice_input("Language: ", list(LANGUAGES.keys()))

        part_title = self.ui.get_text_input("Title of new part: ")
        page_count = self.ui.get_int_input("Page count: ")
        price = self.ui.get_float_input("Price (€): ")

        new_part = {
            "author": book["author"],
            "book_category": book_category,
            "book_size": book_size,
            "language": language,
            "page_count": page_count,
            "price": price,
            "title": part_title,
        }

        book["data"].append(new_part)
        print("New part added successfully.")
        return True

    def _get_first_leaf_book(self, data: BooksData) -> Optional[BookDict]:
        """Get the first leaf-level book (without nested data) for reference."""
        for item in data:
            if "data" not in item:
                return item
            else:
                result = self._get_first_leaf_book(item["data"])
                if result:
                    return result
        return None


class GitManager:
    """Handles git operations."""

    def __init__(self, repo_path: Path):
        """Initialize GitManager with repository path."""
        self.repo_path = repo_path

    def run_command(self, command: List[str]) -> tuple[int, str, str]:
        """Run a git command and return (exit_code, stdout, stderr)."""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def commit_and_push(self, commit_message: str) -> bool:
        """Stage data.txt, commit with message, and push to remote."""
        print("\n" + "=" * 60)
        print("GIT OPERATIONS")
        print("=" * 60)

        # Stage data.txt
        print("\nStaging data.txt...")
        exit_code, stdout, stderr = self.run_command(["git", "add", "data.txt"])
        if exit_code != 0:
            print(f"Error staging file: {stderr}")
            return False
        print("File staged successfully.")

        # Commit
        print(f"\nCommitting with message: {commit_message}")
        exit_code, stdout, stderr = self.run_command(
            ["git", "commit", "-m", commit_message]
        )
        if exit_code != 0:
            print(f"Error committing: {stderr}")
            return False
        print("Commit successful.")

        # Push
        print("\nPushing to remote...")
        exit_code, stdout, stderr = self.run_command(["git", "push"])
        if exit_code != 0:
            print(f"Error pushing: {stderr}")
            return False
        print("Push successful.")

        return True


def run_gen_table(script_path: Path) -> bool:
    """Run the gen_table.py script and return True if successful."""
    print("\n" + "=" * 60)
    print("GENERATING TABLE")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("Table generated successfully!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"Error generating table (exit code {result.returncode}):")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False

    except subprocess.TimeoutExpired:
        print("Error: gen_table.py timed out")
        return False
    except Exception as e:
        print(f"Error running gen_table.py: {e}")
        return False


def main() -> None:
    """Main entry point for the book management system."""
    print("=" * 60)
    print("BOOK MANAGEMENT SYSTEM")
    print("=" * 60)

    # Initialize components
    manager = BookManager()
    ui = UserInterface()
    creator = BookCreator(ui)
    editor = BookEditor(manager, ui)
    git_mgr = GitManager(Path("/save/scripts/report_lulu"))

    # Main menu loop
    while True:
        print("\n" + "=" * 60)
        print("MAIN MENU")
        print("=" * 60)
        print("1. Add new book")
        print("2. Edit existing book")
        print("3. View all books")
        print("4. Save and exit")
        print("0. Exit without saving")

        choice = ui.get_int_input("\nYour choice: ", min_value=0)

        if choice == 0:
            print("\nExiting without saving.")
            sys.exit(0)

        elif choice == 1:
            new_book = creator.add_new_book()
            if new_book:
                manager.books.append(new_book)
                print("\nBook added to collection!")

        elif choice == 2:
            editor.edit_book()

        elif choice == 3:
            print("\n--- All Books ---")
            manager.display_books()

        elif choice == 4:
            # Save and exit flow
            print("\n" + "=" * 60)
            print("SAVE AND EXIT")
            print("=" * 60)

            # Save the data
            manager.save_books()

            # Run gen_table.py
            gen_table_path = Path("/save/scripts/report_lulu/gen_table.py")
            if run_gen_table(gen_table_path):
                # Ask for commit message
                if ui.confirm("\nCommit and push changes?"):
                    commit_msg = ui.get_text_input(
                        "\nEnter commit message (or press Enter for default): ",
                        allow_empty=True,
                    )

                    if not commit_msg:
                        # Generate default commit message based on last operation
                        commit_msg = "Update book database"

                    git_mgr.commit_and_push(commit_msg)
                    print("\nAll operations completed successfully!")
                else:
                    print("\nChanges saved but not committed.")
            else:
                print("\ngen_table.py failed. Changes NOT committed or pushed.")
                print("Data was saved to data.txt but git operations were skipped.")

            sys.exit(0)

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

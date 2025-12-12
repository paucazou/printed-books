# Test Suite for manage_books.py

Comprehensive pytest unit tests for the book management system.

## Overview

This test suite provides extensive coverage for all classes and functions in `manage_books.py`, including:

- **BookManager**: JSON file operations, loading, saving, and book search
- **BookCreator**: Creating single and multi-part books
- **BookEditor**: Editing existing books and adding parts
- **UserInterface**: Input validation and user interactions
- **GitManager**: Git operations (add, commit, push)
- **gen_table execution**: Testing script execution and error handling

## Test Statistics

- **Total Tests**: 117
- **Test Classes**: 8
- **Test Coverage**: Comprehensive coverage of all major code paths

## Running the Tests

### Run All Tests
```bash
python -m pytest test_manage_books.py -v
```

### Run Specific Test Class
```bash
python -m pytest test_manage_books.py::TestBookManager -v
```

### Run Specific Test
```bash
python -m pytest test_manage_books.py::TestBookManager::test_load_books_success -v
```

### Run with Coverage Report (if pytest-cov installed)
```bash
python -m pytest test_manage_books.py --cov=manage_books --cov-report=html
```

### Run Tests Quietly
```bash
python -m pytest test_manage_books.py -q
```

### Run Tests with Detailed Output
```bash
python -m pytest test_manage_books.py -vv
```

## Test Organization

### 1. TestBookManager (11 tests)
Tests for the BookManager class that handles JSON file operations:

- `test_load_books_success`: Loading books from valid JSON file
- `test_load_books_file_not_found`: Handling missing data file
- `test_load_books_invalid_json`: Handling corrupted JSON
- `test_save_books_success`: Saving books to file
- `test_save_books_error`: Handling save errors
- `test_display_books_simple`: Displaying simple books
- `test_display_books_with_nested_data`: Displaying nested book structures
- `test_find_book_by_index_simple_book`: Finding simple books by index
- `test_find_book_by_index_nested_book`: Finding nested books by index
- `test_find_book_by_index_not_found`: Handling invalid indices
- `test_find_book_by_index_boundary`: Testing boundary conditions

### 2. TestUserInterface (20 tests)
Tests for user input validation and interaction:

- Integer input validation (valid, invalid, minimum values, keyboard interrupt)
- Float input validation (valid, invalid, minimum values, keyboard interrupt)
- Choice input (by number, by text, invalid choices, keyboard interrupt)
- Text input (valid, empty allowed/disallowed, whitespace stripping)
- Confirmation prompts (yes/no variations, invalid input)

### 3. TestBookCreator (9 tests)
Tests for creating new books:

- `test_create_simple_book_with_params`: Creating simple books with all parameters
- `test_create_simple_book_with_prompts`: Creating books with user prompts
- `test_create_simple_book_validates_types`: Type validation for page_count and price
- `test_create_multi_part_book`: Creating multi-part book series
- `test_create_multi_part_book_single_part`: Edge case with single part
- `test_add_new_book_single_part_accepted`: Complete workflow with confirmation
- `test_add_new_book_rejected`: User rejecting book creation
- `test_add_new_book_multi_part`: Creating multi-part books interactively

### 4. TestBookEditor (16 tests)
Tests for editing existing books:

- Editing simple book fields (author, title, category, size, language, page count, price)
- Editing multi-part book main title
- Editing multi-part book author (updates all parts)
- Adding new parts to multi-part books
- Canceling edit operations
- Invalid selections
- Helper method tests (get_first_leaf_book, update_author_recursively)

### 5. TestGitManager (9 tests)
Tests for Git operations:

- `test_run_command_success`: Successful git commands
- `test_run_command_failure`: Failed git commands
- `test_run_command_timeout`: Command timeout handling
- `test_run_command_exception`: Exception handling
- `test_commit_and_push_success`: Complete commit and push workflow
- `test_commit_and_push_stage_failure`: Failure at staging
- `test_commit_and_push_commit_failure`: Failure at commit
- `test_commit_and_push_push_failure`: Failure at push
- `test_commit_and_push_uses_correct_repo_path`: Path verification

### 6. TestRunGenTable (6 tests)
Tests for gen_table.py execution:

- `test_run_gen_table_success`: Successful script execution
- `test_run_gen_table_failure`: Script execution failure
- `test_run_gen_table_timeout`: Script timeout
- `test_run_gen_table_exception`: Exception handling
- `test_run_gen_table_uses_correct_interpreter`: Python interpreter verification
- `test_run_gen_table_uses_correct_working_directory`: Working directory verification

### 7. TestIntegration (4 tests)
Integration tests combining multiple components:

- `test_create_and_save_simple_book`: Create and save workflow
- `test_create_and_edit_book`: Create then edit workflow
- `test_multi_part_book_workflow`: Complete multi-part book workflow
- `test_git_workflow_after_save`: Git operations after save

### 8. TestParametrized (33 tests)
Parametrized tests for comprehensive data coverage:

- All book categories (4 tests)
- All book sizes (7 tests)
- All languages (3 tests)
- Various page counts (5 tests)
- Various prices (5 tests)
- Various part counts (5 tests)

### 9. TestErrorHandling (9 tests)
Edge cases and error handling:

- `test_empty_books_list`: Empty book collection
- `test_corrupted_json_structure`: Unexpected JSON structure
- `test_special_characters_in_title`: Special characters handling
- `test_unicode_in_author_name`: Unicode support
- `test_very_long_title`: Long string handling
- `test_zero_price_edge_case`: Zero price validation
- `test_display_books_with_none_books`: Empty display
- `test_find_book_by_index_zero`: Zero index
- `test_find_book_by_index_negative`: Negative index

### 10. TestConstants (3 tests)
Tests for module constants:

- `test_book_categories_defined`: Verify BOOK_CATEGORIES constant
- `test_book_sizes_defined`: Verify BOOK_SIZES constant
- `test_languages_defined`: Verify LANGUAGES constant

## Test Fixtures

Fixtures defined in `conftest.py`:

### Data Fixtures
- `sample_books_data`: Sample book collection for testing
- `temp_data_file`: Temporary data file with sample books
- `simple_book_dict`: Simple book dictionary
- `multi_part_book_dict`: Multi-part book dictionary
- `complex_nested_book`: Complex nested book structure

### Component Fixtures
- `book_manager`: BookManager instance with temp file
- `user_interface`: UserInterface instance
- `book_creator`: BookCreator instance
- `book_editor`: BookEditor instance
- `git_manager`: GitManager instance

### Helper Fixtures
- `project_root`: Project root directory path
- `test_data_dir`: Session-scoped temp directory
- `mock_subprocess_success`: Mock subprocess success result
- `mock_subprocess_failure`: Mock subprocess failure result

## Key Testing Strategies

### 1. Mocking
All tests use `unittest.mock` to mock:
- User input (`builtins.input`)
- File I/O operations
- Subprocess calls for git and gen_table.py
- System exit calls

### 2. Isolation
- Tests use temporary files (pytest's `tmp_path`)
- No modifications to actual `data.txt`
- Each test is independent
- Fixtures reset state between tests

### 3. Coverage Areas
- **Happy path**: Normal successful operations
- **Error paths**: File not found, invalid JSON, subprocess failures
- **Edge cases**: Empty inputs, boundary values, special characters
- **Input validation**: Invalid inputs, type checking, range validation
- **Integration**: Multiple components working together

### 4. Assertions
- Clear assertion messages
- Type checking (isinstance)
- Value checking (equality, ranges)
- Structure validation (dict keys, list lengths)
- Output verification (capsys for stdout)

## Test Data Examples

### Simple Book Structure
```json
{
    "author": "Test Author",
    "book_category": "Music",
    "book_size": "A4",
    "language": "fra",
    "page_count": 100,
    "price": 10.50,
    "title": "Simple Book"
}
```

### Multi-Part Book Structure
```json
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
            "title": "Part 1"
        }
    ]
}
```

## Requirements

- Python 3.7+
- pytest >= 7.0
- unittest.mock (standard library)

Optional:
- pytest-cov (for coverage reports)

## Installation

Install pytest:
```bash
pip install pytest pytest-cov
```

## Common Test Patterns

### Testing with Mock Input
```python
with patch("builtins.input", return_value="test input"):
    result = ui.get_text_input("Prompt: ")
    assert result == "test input"
```

### Testing Subprocess Calls
```python
with patch("subprocess.run", return_value=mock_result):
    result = git_manager.run_command(["git", "status"])
    assert result[0] == 0
```

### Testing File Operations
```python
with patch("builtins.open", mock_open(read_data='{"books": []}')):
    manager.load_books()
```

### Testing System Exit
```python
with pytest.raises(SystemExit) as exc_info:
    manager.load_books()
assert exc_info.value.code == 1
```

## Maintenance

To add new tests:

1. Add test method to appropriate test class
2. Use existing fixtures or create new ones in conftest.py
3. Follow naming convention: `test_<functionality>_<scenario>`
4. Include docstring explaining what the test verifies
5. Run tests to ensure they pass

## CI/CD Integration

For CI/CD pipelines:

```bash
# Run tests with JUnit XML output
python -m pytest test_manage_books.py --junitxml=test-results.xml

# Run tests with coverage and fail if coverage < 80%
python -m pytest test_manage_books.py --cov=manage_books --cov-fail-under=80
```

## Troubleshooting

### Tests fail with "Module not found"
Ensure you're running from the correct directory:
```bash
cd /save/scripts/report_lulu
python -m pytest test_manage_books.py
```

### Tests fail with "fixture not found"
Ensure `conftest.py` is in the same directory as the test file.

### Mocking issues
Make sure to patch at the point of use, not the point of definition.

## Contributing

When adding new features to `manage_books.py`:

1. Write tests first (TDD approach)
2. Ensure all existing tests still pass
3. Aim for high test coverage
4. Test both success and failure scenarios
5. Add parametrized tests for multiple data variations

## License

Same as the main project.

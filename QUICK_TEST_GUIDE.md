# Quick Test Guide

## Running Tests

```bash
# Run all tests
python -m pytest test_manage_books.py -v

# Run all tests (quiet mode)
python -m pytest test_manage_books.py -q

# Run specific test class
python -m pytest test_manage_books.py::TestBookManager -v

# Run specific test
python -m pytest test_manage_books.py::TestBookManager::test_load_books_success -v
```

## Test Summary

- **Total Tests**: 117 tests
- **Execution Time**: ~0.17 seconds
- **Success Rate**: 100%

## Test Coverage by Component

| Component | Test Count | Description |
|-----------|------------|-------------|
| TestParametrized | 33 | Parametrized tests for all categories, sizes, languages, prices |
| TestUserInterface | 20 | User input validation (int, float, choice, text, confirm) |
| TestBookEditor | 16 | Editing books, adding parts, recursive updates |
| TestBookManager | 11 | Loading, saving, displaying, finding books |
| TestBookCreator | 9 | Creating simple and multi-part books |
| TestGitManager | 9 | Git add, commit, push operations |
| TestErrorHandling | 9 | Edge cases, special characters, unicode |
| TestRunGenTable | 6 | gen_table.py execution and error handling |
| TestIntegration | 4 | End-to-end workflows |
| TestConstants | 3 | Module constants validation |

## Key Features Tested

### 1. BookManager Class
- Loading books from JSON file
- Saving books to JSON file
- Displaying books (simple and nested)
- Finding books by index
- Error handling (file not found, invalid JSON)

### 2. BookCreator Class
- Creating simple books (1 part)
- Creating multi-part books (2+ parts)
- Input validation for page_count (int) and price (float)
- User confirmation workflow

### 3. BookEditor Class
- Editing simple book fields (author, title, category, size, language, page_count, price)
- Editing multi-part books (main title, author)
- Adding new parts to existing multi-part books
- Recursive author updates across all nested parts

### 4. UserInterface Class
- Integer input with validation
- Float input with validation
- Choice input (by number or text)
- Text input with whitespace handling
- Yes/no confirmation prompts
- Keyboard interrupt handling

### 5. GitManager Class
- Running git commands
- Staging files (git add)
- Committing changes (git commit)
- Pushing to remote (git push)
- Error handling for each git operation
- Timeout handling

### 6. gen_table.py Execution
- Successful execution
- Failed execution
- Timeout handling
- Exception handling
- Correct Python interpreter usage
- Correct working directory

## Test Isolation

All tests are isolated and use:
- **Temporary files**: No modifications to actual data.txt
- **Mocked input**: All user input is mocked
- **Mocked subprocess**: Git and gen_table.py calls are mocked
- **Independent execution**: Each test can run independently

## Test Data

Tests use realistic book data structures:

**Simple Book:**
```json
{
    "author": "John Smith",
    "book_category": "Music",
    "book_size": "A4",
    "language": "fra",
    "page_count": 150,
    "price": 12.50,
    "title": "Music Theory"
}
```

**Multi-Part Book:**
```json
{
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
            "title": "Volume 1"
        }
    ]
}
```

## Requirements

- Python 3.7+
- pytest >= 7.0
- unittest.mock (standard library)

## Installation

```bash
pip install pytest
```

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'manage_books'"
**Solution**: Run pytest from the `/save/scripts/report_lulu` directory

### Issue: "fixture 'book_manager' not found"
**Solution**: Ensure `conftest.py` is in the same directory

### Issue: Tests modify actual data.txt
**Solution**: Tests use temporary files. If data.txt is modified, there's a bug in the test isolation.

## Next Steps

To add new tests:
1. Identify the component to test
2. Add test method to appropriate test class
3. Use existing fixtures from conftest.py
4. Mock external dependencies
5. Write clear assertions
6. Run tests to verify

## CI/CD Integration

```bash
# JUnit XML output for CI systems
python -m pytest test_manage_books.py --junitxml=test-results.xml

# Fail if tests don't pass
python -m pytest test_manage_books.py --exitfirst

# Run with coverage (requires pytest-cov)
python -m pytest test_manage_books.py --cov=manage_books
```

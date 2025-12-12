# Book Management System - User Guide

## Overview

`manage_books.py` is an interactive Python script for managing the book catalog in `data.txt`. It provides a user-friendly command-line interface for adding new books, editing existing entries, and automatically handling git operations.

## Features

### 1. Add New Books

The script intelligently handles both simple books and multi-volume collections:

- **Single Volume Books**: Creates a simple book entry with all required fields
- **Multi-Volume Collections**: Creates a book with nested "data" array containing all volumes
- **Smart Input Flow**: Asks for common information once, then specific details for each volume

#### Supported Fields

- **Author**: The book's author(s)
- **Book Category**: Music, Religion & Spirituality, Philosophy, History
- **Book Size**: Pocket, Pocket Book, Digest, Executive, US Trade, A5, A4
- **Language**: fra (Français), lat (Latin), eng (Anglais)
- **Title**: Book title (main title for collections, specific title for volumes)
- **Page Count**: Integer value
- **Price**: Decimal value in Euros

### 2. Edit Existing Books

Edit mode allows you to:

- **For Simple Books**: Edit any field (author, title, category, size, language, page count, price)
- **For Multi-Part Books**:
  - Add new volumes to existing collections
  - Edit the main title
  - Edit the author (automatically updates all nested volumes)

### 3. View All Books

Display a hierarchical view of all books in the catalog with proper indentation for nested structures.

### 4. Automatic Git Integration

When you save and exit:

1. The script saves your changes to `data.txt`
2. Runs `gen_table.py` to regenerate the HTML table
3. If `gen_table.py` succeeds:
   - Prompts for a commit message
   - Stages `data.txt`
   - Creates a git commit
   - Pushes to the remote repository
4. If `gen_table.py` fails:
   - Saves the data but skips git operations
   - Displays error messages for debugging

## Usage

### Running the Script

```bash
cd /save/scripts/report_lulu
python3 manage_books.py
```

Or if made executable:

```bash
./manage_books.py
```

### Main Menu Options

```
1. Add new book       - Add a new book to the catalog
2. Edit existing book - Modify or extend existing entries
3. View all books     - Display the entire catalog
4. Save and exit      - Save changes and run git operations
0. Exit without saving - Quit without saving changes
```

## Workflow Examples

### Example 1: Adding a Single Book

```
Your choice: 1

How many parts/volumes are in this book? 1

--- Common Information ---
Author: Marcel Dupré
Book category: 2 (Music)
Book size: 6 (A5)
Language: 1 (fra)
Title: Méthode d'Orgue
Page count: 120
Price (€): 5.50

[Preview shown]
Add this book? y
```

### Example 2: Adding a Multi-Volume Work

```
Your choice: 1

How many parts/volumes are in this book? 3

--- Common Information ---
Author: Saint Thomas d'Aquin
Book category: Religion & Spirituality
Book size: A5
Language: lat
Main title: Summa Theologica

--- Part 1/3 ---
Title of part 1: Prima Pars
Page count: 650
Price (€): 13.50

--- Part 2/3 ---
Title of part 2: Secunda Pars
Page count: 720
Price (€): 14.80

--- Part 3/3 ---
Title of part 3: Tertia Pars
Page count: 580
Price (€): 12.20

[Preview shown]
Add this book? y
```

### Example 3: Adding a Volume to Existing Collection

```
Your choice: 2

Current books:
1. Traité d'harmonie - Kœchlin
  1. Traité d'Harmonie - Tome 1
  2. Traité d'harmonie - Tome 2
2. Principes de morale - Lottin
...

Enter the number of the book to edit: 1

Selected: Traité d'harmonie - Kœchlin

What would you like to do?
1. Add a new part/volume to this book
2. Edit main title
3. Edit author

Your choice: 1

Adding new part to: Traité d'harmonie

Using common information from existing parts:
  Category: Music
  Size: A4
  Language: fra
Use these values for the new part? y

Title of new part: Traité d'harmonie - Tome 3
Page count: 310
Price (€): 11.25
```

### Example 4: Correcting a Mistake

```
Your choice: 2

Enter the number of the book to edit: 15

Selected: Traité de Contrepoint - Gallon & Bitsch

What would you like to edit?
1. Author
2. Title
3. Book Category
4. Book Size
5. Language
6. Page Count
7. Price

Your choice: 7
New price (€): 4.50

Book updated successfully.
```

### Example 5: Saving and Committing

```
Your choice: 4

Data saved successfully to /save/scripts/report_lulu/data.txt

============================================================
GENERATING TABLE
============================================================
Table generated successfully!

Commit and push changes? y

Enter commit message: Ajout: Méthode d'Orgue de Marcel Dupré

============================================================
GIT OPERATIONS
============================================================

Staging data.txt...
File staged successfully.

Committing with message: Ajout: Méthode d'Orgue de Marcel Dupré
Commit successful.

Pushing to remote...
Push successful.

All operations completed successfully!
```

## Input Validation

The script includes comprehensive input validation:

- **Integer Fields**: Only accepts valid integers >= specified minimum
- **Float Fields**: Only accepts valid decimal numbers >= 0
- **Choice Fields**: Accepts either the number or exact text from the list
- **Text Fields**: Ensures non-empty input (unless explicitly allowed)
- **Confirmations**: Only accepts y/yes or n/no

## Error Handling

The script handles various error scenarios:

- **File Not Found**: Exits with clear error message if `data.txt` doesn't exist
- **Invalid JSON**: Reports JSON parsing errors
- **Gen Table Failure**: Skips git operations if table generation fails
- **Git Command Failures**: Reports specific git errors (staging, commit, push)
- **Keyboard Interrupt**: Gracefully handles Ctrl+C to exit
- **Input Errors**: Prompts user to retry invalid inputs

## Data Structure

The script maintains JSON compatibility with the existing structure:

**Simple Book:**
```json
{
    "author": "Author Name",
    "book_category": "Music",
    "book_size": "A5",
    "language": "fra",
    "page_count": 120,
    "price": 5.50,
    "title": "Book Title"
}
```

**Multi-Part Book:**
```json
{
    "author": "Author Name",
    "title": "Collection Title",
    "data": [
        {
            "author": "Author Name",
            "book_category": "Music",
            "book_size": "A5",
            "language": "fra",
            "page_count": 120,
            "price": 5.50,
            "title": "Volume 1"
        },
        ...
    ]
}
```

Books can be nested multiple levels deep (as seen in the Cornelius a Lapide and Fillion entries).

## Technical Details

- **Language**: Python 3.11+
- **Type Hints**: Full type annotations for better code clarity
- **Dependencies**: Only uses Python standard library
- **Encoding**: UTF-8 for proper handling of special characters (œ, é, etc.)
- **JSON Formatting**: 4-space indentation, no ASCII encoding (preserve Unicode)

## Best Practices

1. **Always preview before confirming**: Review the JSON preview before adding books
2. **Use consistent naming**: Follow existing patterns for titles and author names
3. **Test table generation**: The script automatically tests it, but check the output
4. **Write descriptive commit messages**: Include author and title information
5. **Back up data**: Consider backing up `data.txt` before major changes

## Troubleshooting

### Script won't start
- Check Python version: `python3 --version` (should be 3.11+)
- Verify file path: Ensure you're in the correct directory

### Can't find data.txt
- The script expects `/save/scripts/report_lulu/data.txt`
- Check the path is correct and file exists

### gen_table.py fails
- Ensure `table.html` template exists in the same directory
- Check `gen_table.py` runs independently: `python3 gen_table.py`
- Review error messages for specific issues

### Git operations fail
- Ensure git is configured: `git config user.name` and `git config user.email`
- Check remote repository access
- Verify you have permission to push

### Special characters display incorrectly
- Ensure your terminal supports UTF-8
- The script uses UTF-8 encoding by default

## Future Enhancements

Potential improvements for future versions:

- Batch import from CSV or external sources
- Search and filter functionality
- Duplicate detection
- Price and page count statistics
- Validation against existing entries
- Undo/redo functionality
- Export to different formats

## Support

For issues or questions:

1. Check error messages carefully - they're designed to be informative
2. Review this documentation
3. Verify your Python version and environment
4. Test `gen_table.py` independently
5. Check git status manually if needed

## License

This script is part of the report_lulu project.

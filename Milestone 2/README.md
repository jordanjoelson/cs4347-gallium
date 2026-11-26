# Library Management System: Milestone 2

CS 4347 Database Systems, Team Gallium

## Overview

This project is a Library Management System for librarians. The host application is written in Python and uses a SQLite relational database as the DBMS.

## Requirements

| Item | Version / Details |
|---|---|
| Language | Python 3 (tested with Python 3.14.2) |
| DBMS | SQLite 3, through Python's built-in `sqlite3` module |
| Compiler | None needed. Python is interpreted. |
| Third-party modules | None. Only the Python standard library is used (`sqlite3`, `csv`, `os`). |

No database server needs to be installed. SQLite stores the whole database in a single file, `library.db`.

## Files

| File | Purpose |
|---|---|
| `books-1.csv` | Original book data provided for the project (not normalized) |
| `borrowers_ORIGINAL.csv` | Original borrower data provided for the project (not normalized) |
| `normalize.py` | Normalizes the original data into 3NF and writes the four CSV files below |
| `books.csv` | Data for the `BOOK` table |
| `authors.csv` | Data for the `AUTHORS` table |
| `book_authors.csv` | Data for the `BOOK_AUTHORS` table (links books to authors, many-to-many) |
| `borrowers.csv` | Data for the `BORROWER` table |
| `schema.sql` | DDL that creates the six tables, with their primary keys, foreign keys, and constraints |
| `build_db.py` | Creates `library.db` from `schema.sql` and loads the CSV data into the tables |
| `db.py` | Opens a connection to `library.db` with foreign key enforcement turned on |
| `search.py` | Book search and availability |
| `loans.py` | Checking books out and in |
| `borrowers.py` | Creating new borrowers |
| `fines.py` | Calculating, displaying, and paying fines |
| `test_library.py` | Tests every function on a temporary copy of the database |

The normalized CSV files are already included, so running `normalize.py` is optional.

## How to Build the Database

1. Open a terminal in this folder.
2. (Optional) Regenerate the normalized CSV files from the original data:

   ```
   python normalize.py
   ```

3. Create and load the database:

   ```
   python build_db.py
   ```

4. You should see: `SQL Database successfully built and populated!`

This creates `library.db` in the same folder. Running the script again deletes the old `library.db` and builds a fresh copy, so it is always safe to rerun.

`BOOK_LOANS` and `FINES` start empty. Rows are added to them by the application.

## How to Run the Tests

After building the database, run:

```
python test_library.py
```

You should see: `All tests passed.` The tests run on a temporary copy of `library.db`, so the real database is not changed.

## How to Use the Functions

Milestone 2 is the program logic only; the GUI comes in Milestone 3. Each feature is a Python function. To try them, open a Python shell in this folder by running `python`, then import and call the functions as shown below.

When a request breaks a rule (for example, a book that is already checked out), the function raises a `ValueError` with a message explaining why. Every function that changes data runs as a single transaction, so a failed request leaves the database unchanged.

### Book search and availability (`search.py`)

```python
from search import search
search("will")
```

Searches ISBN, title, and author names. The search is case insensitive and matches any part of a word. Each word must match somewhere, so `search("jurassic crichton")` finds *Jurassic Park*. Returns one row per book: `(isbn, title, authors, status)`, where authors is a comma separated list and status is `IN` or `OUT`.

### Book loans (`loans.py`)

```python
from loans import checkout, find_loans, checkin
checkout("0195153445", "ID000001")   # returns the new Loan_id
find_loans("morgan")                 # search by ISBN, card ID, or borrower name
checkin([1])                         # check in 1 to 3 loans by Loan_id
```

- `checkout(isbn, card_id)` creates a `BOOK_LOANS` row with a due date 14 days from today. It fails if the book is already checked out, the borrower already has 3 books out, or the borrower has unpaid fines.
- `find_loans(text)` returns the books that are currently checked out and match the text: `(loan_id, isbn, title, card_id, borrower_name, date_out, due_date)`.
- `checkin(loan_ids)` sets the return date (`Date_in`) to today for each selected loan.

### Borrower management (`borrowers.py`)

```python
from borrowers import create_borrower
create_borrower("Jane Doe", "111-22-3333", "1 Main St, Dallas, TX", "(214) 555-0000")
```

Returns the new card ID. Card IDs are generated automatically in the same format as the existing ones (`ID001001`, `ID001002`, and so on). Name, SSN, and address are required, and a borrower with an SSN that is already in the system is rejected.

### Fines (`fines.py`)

```python
from fines import refresh_fines, show_fines, pay_fines
refresh_fines()                      # calculate fines for all late books
show_fines()                         # unpaid fines, totaled per borrower
show_fines(include_paid=True)        # include fines that were already paid
pay_fines("ID000001")                # pay all of a borrower's fines
```

- `refresh_fines()` charges $0.25 per day late. For a returned book, days late is `Date_in - Due_date`. For a book still out, it is `today - Due_date`. Unpaid fines are updated if the amount changed; paid fines are never changed. In a real library this would run automatically once a day.
- `show_fines()` returns `(card_id, borrower_name, total_fine)`, with fines grouped by borrower.
- `pay_fines(card_id)` pays all of the borrower's unpaid fines at once and returns the total. Partial payments are not allowed, and fines cannot be paid while a late book is still checked out.

## Database Schema

Primary keys are marked with (PK) and foreign keys with (FK).

| Table | Attributes |
|---|---|
| `BOOK` | `Isbn` (PK), `Title` |
| `AUTHORS` | `Author_id` (PK), `Name` |
| `BOOK_AUTHORS` | `Author_id` (PK, FK to `AUTHORS`), `Isbn` (PK, FK to `BOOK`) |
| `BORROWER` | `Card_id` (PK), `Ssn`, `Bname`, `Address`, `Phone` |
| `BOOK_LOANS` | `Loan_id` (PK), `Isbn` (FK to `BOOK`), `Card_id` (FK to `BORROWER`), `Date_out`, `Due_date`, `Date_in` |
| `FINES` | `Loan_id` (PK, FK to `BOOK_LOANS`), `Fine_amt`, `Paid` |

### Changes from the given schema

The schema is backwards compatible with the one provided. We only changed data types and added constraints:

- `Card_id` is stored as text (`VARCHAR(8)`) so it matches the existing card number format, for example `ID000001`.
- `BORROWER.Ssn` has a `UNIQUE` constraint, so a borrower cannot get a second library card.
- `BORROWER.Bname`, `Ssn`, and `Address` are `NOT NULL`, since they are required to create a borrower.
- `BOOK_LOANS.Loan_id` is an `INTEGER PRIMARY KEY`, so SQLite generates a new ID automatically for each loan.
- `FINES.Fine_amt` is `DECIMAL(10,2)`, a fixed-decimal dollar amount with two decimal places.

# Library Management System: Milestone 2

CS 4347 Database Systems, Team Gallium

A Library Management System for librarians. The host application is written in Python and uses SQLite as the DBMS.

## Requirements

- Python 3 (tested with Python 3.14.2). No compiler is needed.
- SQLite, through Python's built-in `sqlite3` module. No database server is needed.
- No third-party modules. Only the Python standard library is used.

## Setup

Open a terminal in this folder and run:

```
python build_db.py
```

This creates `library.db`, a SQLite database file, from `schema.sql` and loads the normalized CSV data. It is safe to rerun; each run builds a fresh copy.

## Project Structure

| File | Purpose |
|---|---|
| `normalize.py` | Normalizes the original data (`books-1.csv`, `borrowers_ORIGINAL.csv`) into the 3NF CSV files. Optional, since the output is already included. |
| `schema.sql` | DDL for the six tables, with primary keys, foreign keys, and constraints |
| `build_db.py` | Creates `library.db` and loads the CSV data |
| `db.py` | Shared database connection (turns on foreign key enforcement) |
| `search.py` | Book search and availability: `search` |
| `loans.py` | Checking books out and in: `checkout`, `find_loans`, `checkin` |
| `borrowers.py` | Borrower management: `create_borrower` |
| `fines.py` | Fines: `refresh_fines`, `show_fines`, `pay_fines` |

Each function raises a `ValueError` with a clear message when a request breaks a rule, such as checking out a book that is already out. Functions that change data run as a single transaction.

## Schema Changes

The schema is backwards compatible with the one provided. We only changed data types and added constraints:

- `Card_id` is text, to match the existing format (`ID000001`).
- `BORROWER.Ssn` is `UNIQUE`, so each borrower has only one library card.
- `Bname`, `Ssn`, and `Address` are `NOT NULL`.
- `BOOK_LOANS.Loan_id` is an `INTEGER PRIMARY KEY`, so SQLite generates it automatically.
- `FINES.Fine_amt` is `DECIMAL(10,2)`, a fixed-decimal dollar amount.

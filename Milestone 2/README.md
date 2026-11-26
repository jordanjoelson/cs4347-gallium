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
| `schema.sql` | DDL that creates the six tables, with their primary keys, foreign keys, and constraints |
| `build_db.py` | Creates `library.db` from `schema.sql` and loads the CSV data into the tables |
| `books.csv` | Data for the `BOOK` table |
| `authors.csv` | Data for the `AUTHORS` table |
| `book_authors.csv` | Data for the `BOOK_AUTHORS` table (links books to authors, many-to-many) |
| `borrowers.csv` | Data for the `BORROWER` table |

The four CSV files are the normalized (3NF) output from Milestone 1.

## How to Build the Database

1. Open a terminal in this folder.
2. Run:

   ```
   python build_db.py
   ```

3. You should see: `SQL Database successfully built and populated!`

This creates `library.db` in the same folder. Running the script again deletes the old `library.db` and builds a fresh copy, so it is always safe to rerun.

`BOOK_LOANS` and `FINES` start empty. Rows are added to them by the application.

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

# Library Management System: Milestone 2

CS 4347 Database Systems, Team Gallium

A Library Management System for librarians. The host application is written in Python and uses SQLite as the DBMS.

## Requirements

- Python 3 (tested with Python 3.14.2). No compiler is needed.
- SQLite, through Python's built-in `sqlite3` module. No database server is needed.
- No third-party modules. Only the Python standard library is used.

## Setup

Open a terminal in this folder and run:

    python build_db.py
    python seed_late_loans.py
    python demo.py

`build_db.py` creates `library.db` from `schema.sql` and loads the CSV data. Each run builds a fresh copy.

`seed_late_loans.py` is only for the demo. Skip it if you only want the empty library.

`demo.py` is the program. The GUI is Milestone 3.

## Menu

    1) Search books
    2) Check out a book
    3) Find and check in loans
    4) Create a borrower
    5) Refresh fines
    6) Show fines
    7) Pay fines
    0) Quit

## Fines demo

1. Choose 5. This creates the fines.
2. Choose 6 and answer n. ID000001 should show $0.75 ($0.50 returned two days late, plus $0.25 still out and due yesterday). ID000002 should not appear.
3. Choose 7 and enter ID000001. It must fail, because one book is still out.
4. Choose 3, search ID000001, and check in the open loan.
5. Choose 5 again. The total is still $0.75, because that book was one day late.
6. Choose 7 and enter ID000001. Payment clears both fines.
7. Choose 6 and answer n. ID000001 is gone. Answer y to see the paid total.

## Project Structure

| File | Purpose |
|---|---|
| `normalize.py` | Builds the 3NF CSV files. Optional. |
| `schema.sql` | The six tables |
| `build_db.py` | Creates `library.db` and loads the CSVs |
| `db.py` | Shared connection |
| `search.py` | `search` |
| `loans.py` | `checkout`, `find_loans`, `checkin` |
| `borrowers.py` | `create_borrower` |
| `fines.py` | `refresh_fines`, `show_fines`, `pay_fines` |
| `demo.py` | The Milestone 2 program |
| `seed_late_loans.py` | Demo loans for the fines test |

Each function raises `ValueError` when a rule is broken. Changes run as one transaction.

## Schema Changes

Backwards compatible. Only types and constraints changed:

- `Card_id` is text, like `ID000001`.
- `BORROWER.Ssn` is `UNIQUE`.
- `Bname`, `Ssn`, and `Address` are `NOT NULL`.
- `BOOK_LOANS.Loan_id` is `INTEGER PRIMARY KEY`.
- `FINES.Fine_amt` is `DECIMAL(10,2)`.
- `FINES.Paid` is 0 or 1.

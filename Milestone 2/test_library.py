# CS 4347 - Team Gallium
# Tests every Milestone 2 function on a temporary copy of library.db,
# so the real database is never changed. Run: python test_library.py
import os
import shutil
import tempfile
from datetime import date, timedelta

import db
from search import search
from loans import checkout, find_loans, checkin
from borrowers import create_borrower
from fines import refresh_fines, show_fines, pay_fines

# Point every module at a temporary copy of the database
temp_dir = tempfile.mkdtemp()
db.DB_PATH = os.path.join(temp_dir, 'library.db')
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library.db'), db.DB_PATH)

def expect_error(func, *args, contains):
    try:
        func(*args)
    except ValueError as e:
        assert contains in str(e), f"Wrong message: {e}"
        return
    raise AssertionError(f"{func.__name__}{args} should have failed")

def days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()

def add_loan(isbn, card_id, date_out, due_date, date_in=None):
    # Insert a loan directly so we can create late loans in the past
    with db.get_connection() as conn:
        return conn.execute(
            "INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in) VALUES (?, ?, ?, ?, ?)",
            (isbn, card_id, date_out, due_date, date_in),
        ).lastrowid

def fine_for(loan_id):
    with db.get_connection() as conn:
        return conn.execute("SELECT Fine_amt, Paid FROM FINES WHERE Loan_id = ?", (loan_id,)).fetchone()

# ---------- Search ----------
results = search("CLASSICAL mythology")
assert ('0195153445', 'Classical Mythology', 'Mark P. O. Morford, Robert J. Lenardon', 'IN') in results
assert len(search("0195153445")) == 1                    # full ISBN gives one result
assert any("Crichton" in r[2] for r in search("crichton"))  # author substring
assert search("   ") == []

# ---------- Checkout ----------
loan1 = checkout("0195153445", "ID000001")
assert search("0195153445")[0][3] == 'OUT'
with db.get_connection() as conn:
    due = conn.execute("SELECT Due_date FROM BOOK_LOANS WHERE Loan_id = ?", (loan1,)).fetchone()[0]
assert due == (date.today() + timedelta(days=14)).isoformat()

expect_error(checkout, "0195153445", "ID000001", contains="not available")  # same borrower
expect_error(checkout, "0195153445", "ID000002", contains="not available")  # other borrower
expect_error(checkout, "XXXXXXXXXX", "ID000001", contains="No book")
expect_error(checkout, "0195153448", "ID999999", contains="No borrower")

checkout("0002005018", "ID000001")
checkout("0060973129", "ID000001")
expect_error(checkout, "0374157065", "ID000001", contains="already has 3")

# ---------- Check in ----------
found = find_loans("mark morgan")                # part of borrower name, any case
assert {r[0] for r in found} >= {loan1}
assert find_loans("ID000001") and find_loans("0195153445")
assert checkin([loan1]) == 1
assert search("0195153445")[0][3] == 'IN'
expect_error(checkin, [loan1], contains="already checked in")
expect_error(checkin, [], contains="at least one")

# ---------- Borrowers ----------
new_id = create_borrower("jane doe", "111-22-3333", "1 Main St, Dallas, TX", "(214) 555-0000")
assert new_id == "ID001001"
assert create_borrower("John Roe", "111-22-4444", "2 Main St, Dallas, TX") == "ID001002"
expect_error(create_borrower, "Someone", "111-22-3333", "3 Main St", contains="already has a library card")
expect_error(create_borrower, "", "999-99-9999", "3 Main St", contains="required")
expect_error(create_borrower, "No Address", "999-99-9999", "  ", contains="required")

# ---------- Fines ----------
# Returned 4 days late: 4 * 0.25 = 1.00
returned_late = add_loan("0393045218", new_id, days_ago(30), days_ago(16), days_ago(12))
# Still out, 10 days late: 10 * 0.25 = 2.50
still_out = add_loan("0399135782", new_id, days_ago(24), days_ago(10))
# Returned on time: no fine
on_time = add_loan("0425176428", "ID000002", days_ago(10), days_ago(1), days_ago(2))

refresh_fines()
assert fine_for(returned_late) == (1.0, 0)
assert fine_for(still_out) == (2.5, 0)
assert fine_for(on_time) is None
assert (new_id, "Jane Doe", 3.5) in show_fines()

# Unpaid fine is updated when the amount changes, never duplicated
with db.get_connection() as conn:
    conn.execute("UPDATE BOOK_LOANS SET Due_date = ? WHERE Loan_id = ?", (days_ago(12), still_out))
refresh_fines()
assert fine_for(still_out) == (3.0, 0)

# Unpaid fines block checkout, and cannot be paid while a book is still out
expect_error(checkout, "0446310786", new_id, contains="unpaid fines")
expect_error(pay_fines, new_id, contains="return all late books")

checkin([still_out])
refresh_fines()
assert pay_fines(new_id) == 4.0                  # pays everything at once
assert fine_for(returned_late)[1] == 1 and fine_for(still_out)[1] == 1
expect_error(pay_fines, new_id, contains="no unpaid fines")

# Paid fines are hidden by default and never changed by refresh
assert all(r[0] != new_id for r in show_fines())
assert (new_id, "Jane Doe", 4.0) in show_fines(include_paid=True)
with db.get_connection() as conn:
    conn.execute("UPDATE BOOK_LOANS SET Due_date = ? WHERE Loan_id = ?", (days_ago(20), returned_late))
refresh_fines()
assert fine_for(returned_late) == (1.0, 1)

# Paying clears the block on checkout
checkout("0446310786", new_id)

shutil.rmtree(temp_dir)
print("All tests passed.")

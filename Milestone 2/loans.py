# CS 4347 - Team Gallium
from datetime import date, timedelta
from db import get_connection

MAX_ACTIVE_LOANS = 3
LOAN_DAYS = 14

def checkout(isbn, card_id):
    """Check out a book to a borrower. Returns the new Loan_id.

    Raises ValueError with a useful message if the checkout is not allowed.
    """
    with get_connection() as conn:
        if not conn.execute("SELECT 1 FROM BOOK WHERE Isbn = ?", (isbn,)).fetchone():
            raise ValueError(f"No book found with ISBN {isbn}.")
        if not conn.execute("SELECT 1 FROM BORROWER WHERE Card_id = ?", (card_id,)).fetchone():
            raise ValueError(f"No borrower found with card ID {card_id}.")

        # 1. The book must not already be checked out (Date_in IS NULL means still out)
        if conn.execute("SELECT 1 FROM BOOK_LOANS WHERE Isbn = ? AND Date_in IS NULL", (isbn,)).fetchone():
            raise ValueError(f"Book {isbn} is not available. It is already checked out.")

        # 2. The borrower may have at most 3 active loans
        active = conn.execute(
            "SELECT COUNT(*) FROM BOOK_LOANS WHERE Card_id = ? AND Date_in IS NULL", (card_id,)
        ).fetchone()[0]
        if active >= MAX_ACTIVE_LOANS:
            raise ValueError(f"Borrower {card_id} already has {MAX_ACTIVE_LOANS} books checked out.")

        # 3. The borrower must not have any unpaid fines
        unpaid = conn.execute("""
            SELECT 1 FROM FINES f
            JOIN BOOK_LOANS l ON l.Loan_id = f.Loan_id
            WHERE l.Card_id = ? AND f.Paid = 0
        """, (card_id,)).fetchone()
        if unpaid:
            raise ValueError(f"Borrower {card_id} has unpaid fines and cannot check out books.")

        # Due date is exactly 14 days from today
        today = date.today()
        due = today + timedelta(days=LOAN_DAYS)
        cursor = conn.execute(
            "INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in) VALUES (?, ?, ?, ?, NULL)",
            (isbn, card_id, today.isoformat(), due.isoformat()),
        )
        return cursor.lastrowid

def find_loans(text):
    """Find books that are currently checked out.

    Matches ISBN, card ID, or any part of the borrower's name (case insensitive).
    Returns a list of (loan_id, isbn, title, card_id, bname, date_out, due_date).
    """
    pattern = f"%{text.strip()}%"
    with get_connection() as conn:
        return conn.execute("""
            SELECT l.Loan_id, l.Isbn, b.Title, l.Card_id, br.Bname, l.Date_out, l.Due_date
            FROM BOOK_LOANS l
            JOIN BOOK b ON b.Isbn = l.Isbn
            JOIN BORROWER br ON br.Card_id = l.Card_id
            WHERE l.Date_in IS NULL
              AND (l.Isbn LIKE ? OR l.Card_id LIKE ? OR br.Bname LIKE ?)
            ORDER BY l.Due_date
        """, (pattern, pattern, pattern)).fetchall()

def checkin(loan_ids):
    """Check in one or more loans by Loan_id (for example the 1 to 3 selected from find_loans).

    Sets Date_in to today. Either all loans are checked in or none are.
    Returns the number of books checked in.
    """
    if not loan_ids:
        raise ValueError("Select at least one loan to check in.")

    today = date.today().isoformat()
    with get_connection() as conn:
        for loan_id in loan_ids:
            updated = conn.execute(
                "UPDATE BOOK_LOANS SET Date_in = ? WHERE Loan_id = ? AND Date_in IS NULL", (today, loan_id)
            ).rowcount
            if updated == 0:
                # Raising here rolls back any loans already checked in above
                raise ValueError(f"Loan {loan_id} does not exist or was already checked in.")
    return len(loan_ids)

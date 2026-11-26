# CS 4347 - Team Gallium
from datetime import date
from db import get_connection

FINE_PER_DAY = 0.25

def refresh_fines():
    """Create or update FINES rows for every late loan. Meant to run once a day.

    Returned late:  fine = (Date_in - Due_date) days * $0.25
    Still out late: fine = (today - Due_date) days * $0.25
    Unpaid fines are updated only if the amount changed. Paid fines are never touched.
    """
    today = date.today().isoformat()
    with get_connection() as conn:
        # COALESCE(Date_in, today) uses today for books that are still out.
        # Multiples of 0.25 are stored exactly, so there is no rounding error.
        conn.execute("""
            INSERT INTO FINES (Loan_id, Fine_amt, Paid)
            SELECT Loan_id,
                   ROUND((julianday(COALESCE(Date_in, :today)) - julianday(Due_date)) * :rate, 2),
                   0
            FROM BOOK_LOANS
            WHERE COALESCE(Date_in, :today) > Due_date
            ON CONFLICT (Loan_id) DO UPDATE
                SET Fine_amt = excluded.Fine_amt
                WHERE Paid = 0 AND Fine_amt != excluded.Fine_amt
        """, {"today": today, "rate": FINE_PER_DAY})

def show_fines(include_paid=False):
    """Total fines per borrower. Paid fines are hidden unless include_paid is True.

    Returns a list of (card_id, bname, total_fine).
    """
    paid_filter = "" if include_paid else "WHERE f.Paid = 0"
    with get_connection() as conn:
        rows = conn.execute(f"""
            SELECT l.Card_id, br.Bname, SUM(f.Fine_amt)
            FROM FINES f
            JOIN BOOK_LOANS l ON l.Loan_id = f.Loan_id
            JOIN BORROWER br ON br.Card_id = l.Card_id
            {paid_filter}
            GROUP BY l.Card_id
            ORDER BY l.Card_id
        """).fetchall()
    return [(card_id, bname, round(total, 2)) for card_id, bname, total in rows]

def pay_fines(card_id):
    """Pay all unpaid fines for a borrower. Returns the total amount paid.

    Partial payments are not allowed, and fines cannot be paid while
    any of the fined books are still checked out.
    """
    with get_connection() as conn:
        unpaid = conn.execute("""
            SELECT f.Fine_amt, l.Date_in
            FROM FINES f
            JOIN BOOK_LOANS l ON l.Loan_id = f.Loan_id
            WHERE l.Card_id = ? AND f.Paid = 0
        """, (card_id,)).fetchall()

        if not unpaid:
            raise ValueError(f"Borrower {card_id} has no unpaid fines.")
        if any(date_in is None for _, date_in in unpaid):
            raise ValueError(f"Borrower {card_id} must return all late books before paying fines.")

        conn.execute("""
            UPDATE FINES SET Paid = 1
            WHERE Paid = 0
              AND Loan_id IN (SELECT Loan_id FROM BOOK_LOANS WHERE Card_id = ?)
        """, (card_id,))
    return round(sum(amount for amount, _ in unpaid), 2)

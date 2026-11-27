# CS 4347 - Team Gallium
# Demo loans so fines can be shown without waiting 14 days.
# Run from this folder, after build_db.py:  python seed_late_loans.py
from datetime import date, timedelta
from db import get_connection

def main():
    today = date.today()
    # card, isbn, days since checkout, days since due date, days since return
    # None means the book is still out.
    # ID000001: returned 2 days late ($0.50) and still out, due yesterday ($0.25)
    # ID000002: returned on the due date (no fine)
    plans = [
        ("ID000001", "0195153445", 20, 6, 4),
        ("ID000001", "0002005018", 15, 1, None),
        ("ID000002", "0060973129", 20, 6, 6),
    ]

    with get_connection() as conn:
        already = conn.execute("SELECT COUNT(*) FROM BOOK_LOANS").fetchone()[0]
        if already:
            raise SystemExit("BOOK_LOANS already has rows. Run python build_db.py first for a fresh demo.")

        for card, isbn, _, _, _ in plans:
            if not conn.execute("SELECT 1 FROM BORROWER WHERE Card_id = ?", (card,)).fetchone():
                raise SystemExit(f"No borrower {card}. Run python build_db.py from this folder.")
            if not conn.execute("SELECT 1 FROM BOOK WHERE Isbn = ?", (isbn,)).fetchone():
                raise SystemExit(f"No book {isbn}. Run python build_db.py from this folder.")

        for card, isbn, out_days, due_days, back_days in plans:
            date_out = today - timedelta(days=out_days)
            due = today - timedelta(days=due_days)
            date_in = None if back_days is None else today - timedelta(days=back_days)
            conn.execute(
                """INSERT INTO BOOK_LOANS
                   (Isbn, Card_id, Date_out, Due_date, Date_in)
                   VALUES (?, ?, ?, ?, ?)""",
                (isbn, card, date_out.isoformat(), due.isoformat(),
                 date_in.isoformat() if date_in else None),
            )

    print("Added 3 demo loans.")
    print("ID000001 Mark Morgan: one book returned 2 days late, one book still out.")
    print("ID000002 Eric Warren: one book returned on time.")
    print("Next: python demo.py")

if __name__ == "__main__":
    main()

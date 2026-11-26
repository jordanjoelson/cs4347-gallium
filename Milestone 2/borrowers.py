# CS 4347 - Team Gallium
from db import get_connection

def create_borrower(name, ssn, address, phone=None):
    """Create a new borrower. Returns the new Card_id (for example ID001001).

    Name, SSN, and address are required. Each SSN may only have one library card.
    Raises ValueError with a useful message if the borrower cannot be created.
    """
    name = (name or "").strip()
    ssn = (ssn or "").strip()
    address = (address or "").strip()
    phone = (phone or "").strip() or None

    if not name or not ssn or not address:
        raise ValueError("Name, SSN, and address are all required.")

    # Same case convention as the normalized data
    name = name.title()

    with get_connection() as conn:
        if conn.execute("SELECT 1 FROM BORROWER WHERE Ssn = ?", (ssn,)).fetchone():
            raise ValueError(f"A borrower with SSN {ssn} already has a library card.")

        # Card IDs are "ID" plus 6 digits, so the text MAX is also the numeric max
        last_id = conn.execute("SELECT MAX(Card_id) FROM BORROWER").fetchone()[0]
        next_number = int(last_id[2:]) + 1 if last_id else 1
        card_id = f"ID{next_number:06d}"

        conn.execute(
            "INSERT INTO BORROWER (Card_id, Ssn, Bname, Address, Phone) VALUES (?, ?, ?, ?, ?)",
            (card_id, ssn, name, address, phone),
        )
    return card_id

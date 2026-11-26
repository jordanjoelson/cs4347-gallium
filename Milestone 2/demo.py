# CS 4347 - Team Gallium
# Text menu for trying the Milestone 2 functions as a librarian would.
# Run: python demo.py  (after python build_db.py)
from search import search
from loans import checkout, find_loans, checkin
from borrowers import create_borrower
from fines import refresh_fines, show_fines, pay_fines

def print_table(headers, rows, max_width=40):
    if not rows:
        print("No results.")
        return
    # Cut long values (like titles) so the table fits on screen
    rows = [[str(v if v is not None else "")[:max_width] for v in row] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(v.ljust(w) for v, w in zip(row, widths)))
    print(f"({len(rows)} rows)")

def do_search():
    rows = search(input("Search (ISBN, title, or author): "))
    print_table(["NO", "ISBN", "TITLE", "AUTHORS", "STATUS"],
                [(i, *r) for i, r in enumerate(rows, 1)])

def do_checkout():
    isbn = input("ISBN: ").strip()
    card_id = input("Card ID: ").strip()
    print(f"Checked out. Loan ID: {checkout(isbn, card_id)}")

def do_checkin():
    rows = find_loans(input("Find loans (ISBN, card ID, or borrower name): "))
    print_table(["LOAN", "ISBN", "TITLE", "CARD", "BORROWER", "OUT", "DUE"], rows)
    if not rows:
        return
    ids = input("Loan IDs to check in, separated by spaces (blank to cancel): ").split()
    if not ids:
        return
    if not all(i.isdigit() for i in ids):
        raise ValueError("Loan IDs must be numbers.")
    print(f"Checked in {checkin([int(i) for i in ids])} book(s).")

def do_new_borrower():
    card_id = create_borrower(input("Name: "), input("SSN: "), input("Address: "), input("Phone (optional): "))
    print(f"Created borrower. Card ID: {card_id}")

def do_refresh_fines():
    refresh_fines()
    print("Fines updated.")

def do_show_fines():
    include_paid = input("Include paid fines? (y/n): ").strip().lower() == "y"
    rows = [(c, n, f"${t:.2f}") for c, n, t in show_fines(include_paid)]
    print_table(["CARD", "BORROWER", "TOTAL"], rows)

def do_pay_fines():
    print(f"Paid ${pay_fines(input('Card ID: ').strip()):.2f}.")

MENU = {
    "1": ("Search books", do_search),
    "2": ("Check out a book", do_checkout),
    "3": ("Find and check in loans", do_checkin),
    "4": ("Create a borrower", do_new_borrower),
    "5": ("Refresh fines", do_refresh_fines),
    "6": ("Show fines", do_show_fines),
    "7": ("Pay fines", do_pay_fines),
}

while True:
    print()
    for key, (label, _) in MENU.items():
        print(f"{key}) {label}")
    print("0) Quit")
    choice = input("> ").strip()
    if choice == "0":
        break
    if choice not in MENU:
        print("Pick a number from the menu.")
        continue
    print()
    try:
        MENU[choice][1]()
    except ValueError as e:
        # Rule violations from the functions (and bad loan ID input) land here
        print(f"Error: {e}")

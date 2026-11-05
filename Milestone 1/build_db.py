# CS 4347 - Team Gallium
import sqlite3
import csv

# Connect to local SQLite database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# 1. Create tables from schema
with open('schema.sql', 'r', encoding='utf-8') as f:
    cursor.executescript(f.read())

# 2. Import Authors
with open('authors.csv', 'r', encoding='utf-8') as f:
    cursor.executemany("INSERT INTO AUTHORS (Author_id, Author) VALUES (?, ?)", csv.reader(f))

# 3. Import Books
with open('books.csv', 'r', encoding='utf-8') as f:
    cursor.executemany("INSERT INTO BOOK (Isbn, Title) VALUES (?, ?)", csv.reader(f))

# 4. Import Book Authors (using the required space in the filename)
with open('book_authors.csv', 'r', encoding='utf-8') as f:
    cursor.executemany("INSERT INTO BOOK_AUTHORS (Isbn, Author_id) VALUES (?, ?)", csv.reader(f))

# 5. Import Borrowers
with open('borrowers.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    # Skip the header row if your borrowers file has one
    next(reader, None) 
    cursor.executemany("INSERT INTO BORROWER (Card_id, Ssn, Bname, Address, Phone) VALUES (?, ?, ?, ?, ?)", reader)

conn.commit()
conn.close()
print("SQL Database successfully built and populated!")
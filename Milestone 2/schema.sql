-- CS 4347 - Team Gallium
CREATE TABLE BOOK (
    Isbn VARCHAR(10) PRIMARY KEY,
    Title VARCHAR(255) NOT NULL
);

CREATE TABLE AUTHORS (
    Author_id INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

CREATE TABLE BOOK_AUTHORS (
    Isbn VARCHAR(10),
    Author_id INT,
    PRIMARY KEY (Author_id, Isbn),
    FOREIGN KEY (Author_id) REFERENCES AUTHORS(Author_id),
    FOREIGN KEY (Isbn) REFERENCES BOOK(Isbn)
);

-- Card_id is text to match the existing IDs (ID000001)
-- Ssn is UNIQUE so each borrower can only have one library card
CREATE TABLE BORROWER (
    Card_id VARCHAR(8) PRIMARY KEY,
    Ssn VARCHAR(11) NOT NULL UNIQUE,
    Bname VARCHAR(255) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    Phone VARCHAR(20)
);

-- INTEGER PRIMARY KEY makes SQLite generate Loan_id automatically
CREATE TABLE BOOK_LOANS (
    Loan_id INTEGER PRIMARY KEY,
    Isbn VARCHAR(10),
    Card_id VARCHAR(8),
    Date_out DATE,
    Due_date DATE,
    Date_in DATE,
    FOREIGN KEY (Isbn) REFERENCES BOOK(Isbn),
    FOREIGN KEY (Card_id) REFERENCES BORROWER(Card_id)
);

CREATE TABLE FINES (
    Loan_id INT PRIMARY KEY,
    Fine_amt DECIMAL(10,2),
    Paid BOOLEAN,
    FOREIGN KEY (Loan_id) REFERENCES BOOK_LOANS(Loan_id)
);

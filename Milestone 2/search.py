# CS 4347 - Team Gallium
from db import get_connection

def search(text):
    """Search books by any combination of ISBN, title, and author(s).

    Case insensitive substring match. Each word in the search must match the
    ISBN, title, or an author, so "jurassic crichton" finds Jurassic Park.
    Returns a list of (isbn, title, authors, status) where status is IN or OUT.
    """
    words = text.split()
    if not words:
        return []

    # One condition per word; SQLite LIKE is case insensitive
    conditions = []
    params = []
    for word in words:
        conditions.append("(b.Isbn LIKE ? OR b.Title LIKE ? OR GROUP_CONCAT(a.Name, ', ') LIKE ?)")
        params += [f"%{word}%"] * 3

    query = f"""
        SELECT b.Isbn,
               b.Title,
               GROUP_CONCAT(a.Name, ', ') AS Authors,
               CASE WHEN EXISTS (SELECT 1 FROM BOOK_LOANS l
                                 WHERE l.Isbn = b.Isbn AND l.Date_in IS NULL)
                    THEN 'OUT' ELSE 'IN' END AS Status
        FROM BOOK b
        LEFT JOIN BOOK_AUTHORS ba ON ba.Isbn = b.Isbn
        LEFT JOIN AUTHORS a ON a.Author_id = ba.Author_id
        GROUP BY b.Isbn
        HAVING {' AND '.join(conditions)}
        ORDER BY b.Title
    """

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()

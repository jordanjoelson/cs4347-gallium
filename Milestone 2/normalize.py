# CS 4347 - Team Gallium

import csv

books_input = 'books-1.csv'
borrowers_input = 'borrowers_ORIGINAL.csv'

books_data = []
seen_isbns = set() # Tracks unique books

authors_dict = {}
book_authors_data = []
seen_relationships = set() # Tracks unique author-book pairs
author_counter = 1

print("Processing books-1.csv...")
with open(books_input, 'r', encoding='utf-8', newline='') as f:
    # csv.reader respects quotes, so "Author A,Author B" stays one field
    reader = csv.reader(f)
    next(reader, None) # Skip the header row

    for row in reader:
        if len(row) < 4: continue

        isbn = row[0].strip()
        title = row[2].strip().title()
        authors_raw = row[3].strip()
        
        # Only add the book if the ISBN hasn't been added yet
        if isbn not in seen_isbns:
            books_data.append([isbn, title])
            seen_isbns.add(isbn)
        
        authors_list = [a.strip().title() for a in authors_raw.split(',')]
        for author in authors_list:
            if not author: continue
            if author not in authors_dict:
                authors_dict[author] = author_counter
                author_counter += 1
            
            author_id = authors_dict[author]
            
            # Only add the relationship if it hasn't been added yet
            # Schema order: Isbn, Author_id
            relationship = (isbn, author_id)
            if relationship not in seen_relationships:
                book_authors_data.append([isbn, author_id])
                seen_relationships.add(relationship)

print(f"Writing {len(books_data)} unique books and {len(authors_dict)} authors...")

with open('books.csv', 'w', newline='', encoding='utf-8') as f:
    csv.writer(f).writerows(books_data)
with open('authors.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for name, a_id in authors_dict.items():
        writer.writerow([a_id, name])
with open('book_authors.csv', 'w', newline='', encoding='utf-8') as f:
    csv.writer(f).writerows(book_authors_data)

print("Processing borrowers_ORIGINAL.csv...")
with open(borrowers_input, 'r', encoding='utf-8') as infile, \
     open('borrowers.csv', 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    # Skip the header row to prevent errors during SQL import
    header = next(reader, None) 
    
    # Original columns: id, ssn, first_name, last_name, email, address, city, state, phone
    # Schema columns:   Card_id, Ssn, Bname, Address, Phone
    for row in reader:
        if len(row) < 9: continue

        card_id, ssn, first, last, _email, street, city, state, phone = [c.strip() for c in row[:9]]

        # Bname is the full name, same case convention as authors
        bname = f"{first} {last}".title()
        # Address combines street, city, and state into one attribute
        address = f"{street}, {city}, {state}"

        writer.writerow([card_id, ssn, bname, address, phone])

print("Normalization complete.")
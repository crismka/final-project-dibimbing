DROP TABLE IF EXISTS goodread_books;
CREATE TABLE IF NOT EXISTS goodread_books (
    bookID INTEGER,
    title TEXT,
    authors TEXT,
    average_rating TEXT,
    isbn TEXT,
    isbn13 TEXT,
    language_code TEXT,
    num_pages TEXT,
    ratings_count INTEGER, 
    text_review_count INTEGER,
    publication_date TEXT, 
    publisher TEXT
);
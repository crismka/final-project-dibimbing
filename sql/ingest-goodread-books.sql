COPY goodread_books FROM '/data/goodread_books.csv' DELIMITER AS ',' CSV HEADER;
SELECT * FROM goodread_books LIMIT 5;
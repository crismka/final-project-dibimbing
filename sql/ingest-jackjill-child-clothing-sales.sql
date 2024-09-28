COPY child_clothing_sales FROM '/data/jackjill_clothing_child_clothing_sales.csv' DELIMITER AS ',' CSV HEADER;
SELECT * FROM child_clothing_sales LIMIT 5;
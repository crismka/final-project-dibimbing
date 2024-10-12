import pyspark
import os
from dotenv import load_dotenv
from pathlib import Path
from pyspark.sql.types import *
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark import StorageLevel
from pyspark.sql.window import Window
from pyspark.sql.functions import col


# Load environment variables from the .env file
dotenv_path = Path('/opt/app/.env')
load_dotenv(dotenv_path=dotenv_path)

# Extract PostgreSQL database connection details from the environment
postgres_host = os.getenv('POSTGRES_CONTAINER_NAME')
postgres_dw_db = os.getenv('POSTGRES_DW_DB')
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')

# Construct the JDBC URL for PostgreSQL connection
jdbc_url = f'jdbc:postgresql://{postgres_host}/{postgres_dw_db}'
print(jdbc_url)

# Define properties required for JDBC connection
jdbc_properties = {
    'user': postgres_user,
    'password': postgres_password,
    'driver': 'org.postgresql.Driver',
    'stringtype': 'unspecified'
}

# Initialize Spark session and configure PostgreSQL JDBC driver
spark = SparkSession.builder \
    .appName("Dibimbing") \
    .config("spark.jars", "/opt/postgresql-42.2.18.jar") \
    .config("spark.driver.extraClassPath", "/opt/postgresql-42.2.18.jar") \
    .config("spark.executor.extraClassPath", "/opt/postgresql-42.2.18.jar") \
    .getOrCreate()

# Load book dataset from CSV file, using a predefined schema
path_csv_datasource = os.getenv('CSV_DATASOURCE')
schema = StructType([
    StructField("bookID", IntegerType(), True),
    StructField("title", StringType(), True),
    StructField("authors", StringType(), True),
    StructField("average_rating", StringType(), True),
    StructField("isbn", StringType(), True),
    StructField("isbn13", StringType(), True),
    StructField("language_code", StringType(), True),
    StructField("num_pages", DoubleType(), True),
    StructField("ratings_count", DoubleType(), True),
    StructField("text_reviews_count", IntegerType(), True),
    StructField("publication_date", StringType(), True),
    StructField("publisher", StringType(), True)
])

goodreads_df = spark.read.csv(f"{path_csv_datasource}", header=True, schema=schema)

# Remove unnecessary columns 'isbn' and 'isbn13' from the DataFrame
goodreads_drop_isbn_isbn13_df = goodreads_df.drop("isbn", "isbn13")

# Filter records with valid average ratings and non-zero ratings count, remove duplicates
goodreads_filter_avg_rate_df = goodreads_drop_isbn_isbn13_df \
    .filter(col("average_rating").rlike("^[0-9]+(\\.[0-9]+)?$") & (col("ratings_count") != 0)) \
    .dropDuplicates(["bookID"])

# Clean and transform data
goodread_cleaned_df = goodreads_filter_avg_rate_df \
       .withColumn("publication_year", F.year(F.to_date("publication_date", "M/d/yyyy"))) \
       .withColumn("title", F.regexp_replace(F.col("title"), r"\s{2,}", " ")) \
       .withColumn("authors", F.regexp_replace(F.col("authors"), r"\s{2,}", " ")) \
       .withColumn("title", F.upper(F.col("title"))) \
       .withColumn("authors", F.upper(F.col("authors"))) \
       .withColumn("language_code", F.upper(F.col("language_code"))) \
       .withColumn("publisher", F.upper(F.col("publisher"))) \
       .withColumn("average_rating", F.col("average_rating").cast(DoubleType()))

# Cache the cleaned DataFrame for efficient reuse
goodread_cleaned_df.cache()

# Calculate and round the correlation between average rating and number of pages
correlation_rating_num_pages = goodread_cleaned_df.stat.corr("average_rating", "num_pages")
correlation_rating_num_pages = round(correlation_rating_num_pages, 2)

# Duplicate correlation logic (should be refactored)
correlation_rating_publication_year = goodread_cleaned_df.stat.corr("average_rating", "publication_year")
correlation_rating_publication_year = round(correlation_rating_publication_year, 2)

# Create a DataFrame for correlation results and write it to PostgreSQL
correlation_rating_num_pages_df = spark.createDataFrame(
    [(correlation_rating_num_pages,)],
    ["correlation_rating_num_pages"]
)

correlation_rating_publication_year_df = spark.createDataFrame(
    [(correlation_rating_publication_year,)],
    ["correlation_rating_publication_year"]
)

# Write correlation results to PostgreSQL
correlation_rating_num_pages_df.write.jdbc(
    url=jdbc_url,
    table="correlation_rating_num_pages",  
    mode="overwrite",
    properties=jdbc_properties
)

correlation_rating_publication_year_df.write.jdbc(
    url=jdbc_url,
    table="correlation_rating_publication_year",  
    mode="overwrite",
    properties=jdbc_properties
)

# Create window spec for top-rated books per publication year
window_publication_year_avg_rating = Window.partitionBy("publication_year").orderBy(F.desc("average_rating"))

# Extract the highest-rated book per year and write to PostgreSQL
top_rated_books_per_year_df = goodread_cleaned_df.withColumn("rank_number", F.rank().over(window_publication_year_avg_rating)) \
    .filter((F.col("rank_number") == 1) & (F.col("publication_year").isNotNull())) \
    .drop("rank_number") \
    .orderBy(F.col("publication_year").desc())

top_rated_books_per_year_df.write.jdbc(
    url=jdbc_url,
    table="top_rated_books_per_year",  
    mode="overwrite",
    properties=jdbc_properties
)

# Create window spec for most-rated books per publication year
window_publication_year_ratings_count = Window.partitionBy("publication_year").orderBy(F.desc("ratings_count"))

# Extract the most-rated book per year and write to PostgreSQL
most_rated_books_per_year_df = goodread_cleaned_df.withColumn("rank_number", F.rank().over(window_publication_year_ratings_count)) \
    .filter((F.col("rank_number") == 1) & (F.col("publication_year").isNotNull())) \
    .drop("rank_number") \
    .orderBy(F.col("publication_year").desc())

most_rated_books_per_year_df.write.jdbc(
    url=jdbc_url,
    table="most_rated_books_per_year",  
    mode="overwrite",
    properties=jdbc_properties
)

# Create window spec for most-reviewed books per publication year
window_publication_year_text_reviews_count = Window.partitionBy("publication_year").orderBy(F.desc("text_reviews_count"))

# Extract the most-reviewed book per year and write to PostgreSQL
most_reviewed_books_per_year_df = goodread_cleaned_df.withColumn("rank_number", F.rank().over(window_publication_year_text_reviews_count)) \
    .filter((F.col("rank_number") == 1) & (F.col("publication_year").isNotNull())) \
    .drop("rank_number") \
    .orderBy(F.col("publication_year").desc())

most_reviewed_books_per_year_df.write.jdbc(
    url=jdbc_url,
    table="most_reviewed_books_per_year",  
    mode="overwrite",
    properties=jdbc_properties
)

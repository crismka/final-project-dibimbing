import pyspark
import os
from dotenv import load_dotenv
from pathlib import Path
from pyspark.sql.types import *
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark import StorageLevel
from pyspark.sql.window import Window
from pyspark.sql.functions import to_date, date_format, col, count, when,lag, sum, countDistinct



dotenv_path = Path('/opt/app/.env')
load_dotenv(dotenv_path=dotenv_path)


#error in airflow because unable to read the postgres_dw_db (read as null) 
postgres_host = os.getenv('POSTGRES_CONTAINER_NAME')
postgres_dw_db = os.getenv('POSTGRES_DW_DB')
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')

#error in airflow while initiate and create spark context then spark session 
#set spark using sparksession.builder
spark = SparkSession.builder \
    .appName("Dibimbing") \
    .config("spark.jars", "/opt/postgresql-42.2.18.jar") \
    .config("spark.driver.extraClassPath", "/opt/postgresql-42.2.18.jar") \
    .config("spark.executor.extraClassPath", "/opt/postgresql-42.2.18.jar") \
    .getOrCreate()

path_csv_datasource = os.getenv('CSV_DATASOURCE')
goodread_books_data_df = spark.read.csv(f"{path_csv_datasource}", header=True)

goodread_books_data_df.show(5)

# goodread_books_data_df.printSchema()


# #configure the jdbc_properties
# jdbc_url = f'jdbc:postgresql://{postgres_host}/{postgres_dw_db}'
# print(jdbc_url)
# jdbc_properties = {
#     'user': postgres_user,
#     'password': postgres_password,
#     'driver': 'org.postgresql.Driver',
#     'stringtype': 'unspecified'
# }


# #read the table from postgresql 
# goodread_books_data_df = spark.read.jdbc(
#     jdbc_url,
#     'public.goodread_books',
#     properties=jdbc_properties
# )


# # goodread_books_data_df.printSchema()

# non_numeric_rows = goodread_books_data_df.filter(~col("average_rating").rlike("^[0-9]+(\.[0-9]+)?$"))

# # non_numeric_rows.printSchema()
# non_numeric_rows.show(5)

# correlation_rating_pages = goodread_books_data_df.stat.corr("average_rating", "num_pages")
# print(f"Correlation between average rating and number of pages: {correlation_rating_pages}")

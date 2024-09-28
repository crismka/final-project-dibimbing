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


#error in airflow because unable to read the postgres_host and postgres_dw_db (read as null) 
#therefore those variable are being hard code
postgres_host = os.getenv('POSTGRES_CONTAINER_NAME')
postgres_dw_db = 'warehouse'
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


#configure the jdbc_properties
jdbc_url = f'jdbc:postgresql://{postgres_host}/{postgres_dw_db}'
print(jdbc_url)
jdbc_properties = {
    'user': postgres_user,
    'password': postgres_password,
    'driver': 'org.postgresql.Driver',
    'stringtype': 'unspecified'
}


#read the table from postgresql 
retail_df = spark.read.jdbc(
    jdbc_url,
    'public.child_clothing_sales',
    properties=jdbc_properties
)

retail_df.show()
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, sum as _sum, window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

# NOTE: To run this, you need the Spark Kafka package:
# spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 streaming/spark_streaming.py

def run_streaming():
    spark = SparkSession.builder \
        .appName("RetailSalesStreaming") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # 1. Define the schema of the incoming Kafka JSON messages
    # Example message: {"order_id": 999, "product_id": 101, "amount": 50000, "timestamp": "2023-10-01T10:00:00.000Z"}
    schema = StructType([
        StructField("order_id", IntegerType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("amount", DoubleType(), True),
        StructField("timestamp", TimestampType(), True)
    ])

    # 2. Read stream from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "live_orders") \
        .option("startingOffsets", "latest") \
        .load()

    # 3. Parse the JSON from the Kafka 'value' column
    parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

    # 4. Perform a tumbling window aggregation (Total sales per minute)
    windowed_sales = parsed_df \
        .withWatermark("timestamp", "1 minute") \
        .groupBy(
            window(col("timestamp"), "1 minute")
        ) \
        .agg(_sum("amount").alias("total_sales"))

    # 5. Write the stream output to the console for learning purposes
    query = windowed_sales \
        .writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    print("Starting PySpark Structured Streaming Job...")
    print("Listening to Kafka topic: 'live_orders' on localhost:9092")
    run_streaming()

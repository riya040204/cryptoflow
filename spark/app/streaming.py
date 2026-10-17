
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, to_timestamp, from_unixtime
)
from pyspark.sql.types import (
    StructType, StructField, StringType,
    DoubleType, LongType
)

spark = (
    SparkSession.builder
    .appName("CryptoFlowStreaming")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("symbol", StringType()),
    StructField("price", DoubleType()),
    StructField("volume", DoubleType()),
    StructField("price_change_percent", DoubleType()),
    StructField("timestamp", LongType()),
])

events = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:29092")
    .option("subscribe", "crypto-prices")
    .option("startingOffsets", "latest")
    .load()
)

parsed = (
    events
    .select(
        from_json(col("value").cast("string"), schema).alias("data")
    )
    .select("data.*")
    .filter(
        col("symbol").isNotNull()
        & (col("price") > 0)
        & col("timestamp").isNotNull()
    )
    .withColumn(
        "event_time",
        to_timestamp(from_unixtime(col("timestamp")))
    )
    .withColumn("exchange", col("symbol"))
)

def save_to_postgres(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    output = batch_df.select(
        "symbol", "exchange", "price", "volume", "event_time"
    )

    (
        output.write
        .format("jdbc")
        .option(
            "url",
            "jdbc:postgresql://postgres:5432/cryptoflow"
        )
        .option("dbtable", "crypto_prices")
        .option("user", "cryptoflow")
        .option("password", "cryptoflow")
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )

query = (
    parsed.writeStream
    .foreachBatch(save_to_postgres)
    .option("checkpointLocation", "/tmp/cryptoflow-checkpoint")
    .start()
)

query.awaitTermination()

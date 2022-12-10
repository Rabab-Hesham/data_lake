import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['default']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['default']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    # get filepath to song data file
    song_data = "s3://udacity-dend/song_data"
    
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df.select('song_id', 'title', 'artist_id', 'duration', 'year').dropDuplicates(['song_id'])
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.parquet(os.path.join(output_data, "songs"), mode="overwrite", partitionBy=[('year' ,'artist')])

    # extract columns to create artists table
    artists_table = df.select('artist_id', 'artist_name', 'artist_location','artist_latitude','artist_longitude').dropDuplicates()
    
    # write artists table to parquet files
    artists_table.write.mode("overwrite").parquet(os.path.join(output_data, 'artists'))


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    log_data = "s3://udacity-dend/log_data"

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.where(df.page == 'NextSong')

    # extract columns for users table    
    #artists_table = 
    users_table = df.selectExpr(['user_id', 'firstName as first_name', 'lastName as last_name', 'gender', 'level', 'ts'])
    
    # write users table to parquet files
    #artists_table
                                
    users_table.write.parquet(os.path.join(output_data, "users"), mode="overwrite")
    
    
    #create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: datetime.fromtimestamp((x/1000.0)), TS.TimestampType())
    df = df.withColumn("time_stamp", F.to_timestamp("ts"))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: str(datetime.fromtimestamp(int(x) / 1000.0)))
    df = df.withColumn("datetime", get_datetime(df.ts))
    
    # extract columns to create time table
    time_table = log_df.selectExpr(
        "timestamp as start_time",
        "hour(timestamp) as hour",
        "dayofmonth(timestamp) as day",
        "weekofyear(timestamp) as week",
        "month(timestamp) as month",
        "year(timestamp) as year",
        "dayofweek(timestamp) as weekday") 
    
    # write time table to parquet files partitioned by year and month
    time_table.write.parquet(os.path.join(output_data, "time"), mode="overwrite", partitionBy=[('year' ,'month')])

    # read in song data to use for songplays table
    song_df = spark.read.json('s3://udacity-dend/song_data', schema = song_schema)

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = df.join(song_df, df['song'] == song_df['title'])

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.parquet(os.path.join(output_data, "songplays"), mode="overwrite", partitionBy=[('year' ,'month')])


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "./Results/"
                                
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()

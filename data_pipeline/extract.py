import pandas as pd
import os
import argparse
import io
from pathlib import Path
from minio import Minio
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pytz
from datetime import datetime, timedelta, timezone

def get_hour(x):
  x = x/1000
  x = datetime.fromtimestamp(x)
  return x.hour

def get_day(x):
  x = x/1000
  x = datetime.fromtimestamp(x)
  return x.day

def get_month(x):
  x = x/1000
  x = datetime.fromtimestamp(x)
  return x.month

def get_year(x):
  x = x/1000
  x = datetime.fromtimestamp(x)
  return x.year

def save_to_minio_partitioned(df, minio_client, bucket_name):
    """
    Lưu DataFrame vào MinIO dưới dạng parquet với partition theo year/month/day/hour
    """
    # Tạo bucket nếu chưa tồn tại
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' đã được tạo")
    
    # Thêm các cột partition
    df['year'] = df['Open_time'].apply(get_year)
    df['month'] = df['Open_time'].apply(get_month)
    df['day'] = df['Open_time'].apply(get_day)
    df['hour'] = df['Open_time'].apply(get_hour).astype(int)
    df['datetime'] = df['Open_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
    df['date'] = df['Open_time'].apply(lambda x: datetime.fromtimestamp(x / 1000).date())
    print(df)
    # Group theo partition date và lưu từng file
    grouped = df.groupby(['date', 'hour'])

    for (date, hour), group in grouped:
        # Tạo đường dẫn partition
        partition_path = f"raw/date={date}/hour={hour:02d}"
        filename = f"data.parquet"
        object_name = f"{partition_path}/{filename}"
        
        # Loại bỏ các cột partition khỏi data (vì đã có trong path)
        data_to_save = group.drop(columns=['date', 'hour'])
        
        # Convert DataFrame to parquet bytes
        parquet_buffer = io.BytesIO()
        data_to_save.to_parquet(parquet_buffer, engine='pyarrow', index=False)
        parquet_buffer.seek(0)
        
        # Upload to MinIO
        try:
            minio_client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=parquet_buffer,
                length=len(parquet_buffer.getvalue()),
                content_type='application/octet-stream'
            )
        except Exception as e:
            print(f"Lỗi khi lưu {object_name}: {e}")
    

def get_data(api_key, api_secret, minio_client, bucket_name, start_date, end_date):
    client = Client(api_key, api_secret, testnet=False)
    print("start_date          :", start_date)
    print("end_date            :", end_date)

    _start = datetime.fromtimestamp(start_date/1000 - 25200).strftime("%Y-%m-%d %H:%M:%S")
    _end = datetime.fromtimestamp(end_date/1000 - 25200).strftime("%Y-%m-%d %H:%M:%S")
    print(f"Đang lấy dữ liệu BTC từ {_start} đến {_end}")

    klines = client.get_historical_klines(symbol ="BTCUSDT", interval='1h', start_str=_start, end_str=_end)

    df = pd.DataFrame(klines, columns =["Open_time", "Open", "High", "Low", "Close", "Volume", 
                                        "Close_time", "Quote_asset_volume", "Number_of_trades",
                                        "Taker_buy_base_asset_volume", "Taker_buy_base_quote_volume", "Ignore"])
    
    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].apply(pd.to_numeric)

    df["Open_time"] = df["Open_time"].apply(lambda x : ((x + 25200000)))
    df["date"] = df["Open_time"].apply(lambda x : datetime.fromtimestamp(x/1000+ 25200))
    print("-"*100)
    print(df )
    print("-"*100)
    # Lưu vào MinIO
    save_to_minio_partitioned(df, minio_client, bucket_name)

    return df

# 1760504400 000
# 1760504400

#      25 200 000 
# 1760517720 000
import pandas as pd
import numpy as np
import os
import argparse
import io
from datetime import datetime, timedelta
from minio import Minio
from pandas.api.indexers import FixedForwardWindowIndexer
import pyarrow.dataset as ds


import pyarrow.dataset as ds
import pyarrow.fs as fs

def read_data_from_minio(s3_path, storage_options, start_date, end_date):
    # Khởi tạo kết nối MinIO qua S3FileSystem
    s3 = fs.S3FileSystem(
        access_key=storage_options["key"],
        secret_key=storage_options["secret"],
        endpoint_override=storage_options["endpoint_url"],
        scheme="http" if not storage_options.get("use_ssl", False) else "https",
    )

    # Tạo dataset
    dataset = ds.dataset(s3_path, format="parquet", filesystem=s3)

    # Lọc dữ liệu theo thời gian
    filter_expr = (ds.field("Open_time") >= start_date) & (ds.field("Open_time") <= end_date)

    # Đọc dữ liệu
    table = dataset.to_table(filter=filter_expr, use_threads=True, 
                             )

    df = table.to_pandas()
    return df


def read_raw_data_from_minio(bucket_name, prefix="raw", start_date=None, end_date=None, minio_endpoint='minio:9000'):

    # Sử dụng pandas read_parquet với S3 storage options và filters
    # Setup storage options for MinIO
    storage_options = {
        'key': 'minio_user',
        'secret': 'minio_password', 
        'endpoint_url': minio_endpoint,
        'use_ssl': False
    }
    
    # Tạo S3 path
    s3_path = f"{bucket_name}/{prefix}/"
    print("s3_path :", s3_path)
    # Đọc với pandas và áp dụng filters
    # Convert date to string format for comparison
    print("start_date :", start_date)
    print("end_date :", end_date)

    print("storage_options :", storage_options)

    df = read_data_from_minio(s3_path, storage_options, start_date, end_date)
    print("df.shape :", df.shape)
    # Sắp xếp theo thời gian
    df = df[df['Open_time'] >= start_date]
    df = df.sort_values('Open_time').reset_index(drop=True)
    
    return df

def get_hour(x):
   x = x/1000
   x = datetime.fromtimestamp(x)
   return x.hour

def get_day(x):
  x = x/1000
  x = datetime.fromtimestamp(x)
  return x.day

def save_processed_data_to_minio(df, minio_client, bucket_name):
    """
    Lưu dữ liệu đã transform vào MinIO dưới dạng parquet với partition theo year/month/day/hour
    """
    
    # Tạo bucket nếu chưa tồn tại
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' đã được tạo")
    
    df['date'] = df['Open_time'].apply(lambda x: datetime.fromtimestamp(x / 1000).date())
    df['hour'] = df['Open_time'].apply(get_hour).astype(int)

    print("df.columns :", df.columns)
    # Group theo partition và lưu từng file
    grouped = df.groupby(['date', 'hour'])

    for (date, hour), group in grouped:
        # Tạo đường dẫn partition cho processed data
        partition_path = f"processed/date={date}/hour={hour:02d}"
        filename = f"features.parquet"
        object_name = f"{partition_path}/{filename}"
        
        # Loại bỏ các cột partition khỏi data (vì đã có trong path) nhưng giữ lại datetime và date
        data_to_save = group.drop(columns=['date', 'hour'], errors='ignore')
        # Đảm bảo giữ lại datetime và date trong file được lưu
        if 'datetime' in group.columns:
            data_to_save['datetime'] = group['datetime']
        if 'date' in group.columns:
            data_to_save['date'] = group['date']
        
        # Convert DataFrame to parquet bytes
        parquet_buffer = io.BytesIO()
        data_to_save.to_parquet(parquet_buffer, engine='pyarrow', index=False)
        parquet_buffer.seek(0)
        
        # Upload to MinIO
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=parquet_buffer,
            length=len(parquet_buffer.getvalue()),
            content_type='application/octet-stream'
        )

def mean(values):
   return sum(values)/float(len(values))


def covariance(x, mean_x, y, mean_y):
   covar = 0.0
   for i in range(len(x)):
       covar += (x[i] - mean_x)*(y[i] - mean_y)
   return covar


def variance(values, mean):
   return sum([(x-mean)**2 for x in values])


def coefficients(Xs, Ys):
   x_mean = mean(Xs)
   y_mean = mean(Ys)
   a = covariance(Xs, x_mean, Ys, y_mean) / (variance(Xs, x_mean)+0.001)
   b = y_mean - a * x_mean
   return [a, b]


def cal_delta(dataframes, num_of_times):
   ser = (dataframes["Close"] - dataframes["Open"].shift(num_of_times-1))/dataframes["Open"].shift(num_of_times-1)
   ser = ser.fillna(0)
   return ser


def cal_trend_score(ser):
   times = range(0, len(ser))
   ser = ser.tolist()
   a, b = coefficients(times, ser)
   first_prices = a*times[0]+b
   last_prices = a*times[len(ser)-1]+b
   delta = ((last_prices-first_prices)/(first_prices+0.01))*100
   return delta


def upper_shadow(df):
   return df['High'] - np.maximum(df['Close'], df['Open'])


def lower_shadow(df):
   return np.minimum(df['Close'], df['Open']) - df['Low']


def EMA(df, label, num_of_times):
   K = 2 / (num_of_times+1)
   return (df[label] * K)+(df[label].shift(-1) * (1 - K))


def SMA(df, label, num_of_times):
   return df[label].rolling(window = num_of_times).mean()


def DCup(df, label, num_of_times):
   return df[label].rolling(window = num_of_times).max()


def DCdown(df, label, num_of_times):
   return df[label].rolling(window = num_of_times).min()


def DCmid(df, label, num_of_times):
   return (df[label].rolling(window = num_of_times).max() + df[label].rolling(window = num_of_times).min() )/2


def corr(df,label_x,label_y):
   return df[label_x]/ df[label_y]


def VWAP(df,num_of_times):
   df_TPV = (df["High"] + df["Low"] + df["Close"])/3
   return df_TPV.rolling(window = num_of_times).sum()/df["Volume"].rolling(num_of_times).sum()


def BollingerBasis(df, num_of_times):
   return df["Close"].rolling(window = num_of_times).mean()


def BollingerUpper(df, num_of_times):
   return df["BollingerBasis"] + 2*df["Close"].rolling(window = num_of_times).std()


def BollingerLower(df, num_of_times):
   return df["BollingerBasis"] - 2*df["Close"].rolling(window = num_of_times).std()


def RSI(df, num_of_times):

   df_UpChange = df["Close"]-df["Close"].shift(-1)
   df_UpChange[df_UpChange<0] = 0
   df_DownChange = df["Close"]-df["Close"].shift(-1)
   df_DownChange[df_UpChange>0] = 0
   RS = df_UpChange.rolling(window = num_of_times).mean() / df_DownChange.rolling(window = num_of_times).mean()

   return 100 - 100 / (1 + RS)


def generate_features(dataframes):
    """
    Tạo các features từ dữ liệu raw
    """
    # Cố định num_of_times = 4
    num_of_times = 4
    
    # Tạo cột datetime từ Open_time nếu chưa có
    if 'datetime' not in dataframes.columns:
        dataframes['datetime'] = pd.to_datetime(dataframes['Open_time'], unit='ms')
        
    # --- Các chỉ báo kỹ thuật ---
    dataframes["EMA"] = EMA(df=dataframes, label="Close", num_of_times=num_of_times)
    dataframes["SMA"] = SMA(df=dataframes, label="Close", num_of_times=num_of_times)
    dataframes["VWAP"] = VWAP(df=dataframes, num_of_times=num_of_times)
    dataframes["RSI"] = RSI(df=dataframes, num_of_times=num_of_times)
    dataframes["DCdown"] = DCdown(df=dataframes, label="Close", num_of_times=num_of_times)
    dataframes["DCup"] = DCup(df=dataframes, label="Close", num_of_times=num_of_times)
    dataframes["DCmid"] = DCmid(df=dataframes, label="Close", num_of_times=num_of_times)
    dataframes["BollingerBasis"] = BollingerBasis(df=dataframes, num_of_times=num_of_times)
    dataframes["BollingerUpper"] = BollingerUpper(df=dataframes, num_of_times=num_of_times)
    dataframes["BollingerLower"] = BollingerLower(df=dataframes, num_of_times=num_of_times)
    dataframes["target"] = dataframes["Close"].shift(-1)

    # --- Tạo trend features ---
    for num_of_time in range(1, num_of_times):
        indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=num_of_time)
        
        # ===== Tính xu hướng TƯƠNG LAI (label) =====
        future_trend_col_name = "Future_trend_{}_{}h".format("Open", num_of_time)
        dataframes[future_trend_col_name] = dataframes["Open"].rolling(indexer).apply(cal_trend_score)
        dataframes[f"{future_trend_col_name}_flag"] = (dataframes[future_trend_col_name] >= 0).astype(int)

        # ===== Tính xu hướng QUÁ KHỨ (feature) =====
        past_trend_col = f"Past_trend_Open_{num_of_time}h"
        dataframes[past_trend_col] = dataframes["Open"].rolling(window=num_of_time).apply(cal_trend_score)
        dataframes[f"{past_trend_col}_flag"] = (dataframes[past_trend_col] >= 0).astype(int)

    return dataframes

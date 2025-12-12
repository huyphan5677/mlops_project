import pandas as pd
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV
import argparse
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_pipeline.transform import read_raw_data_from_minio
from data_pipeline.load import insert_data_postgres
from datetime import datetime, timedelta

mode = 'full_pipeline'
minio_host = 'http://172.16.206.40/:9000'
minio_access_key = 'admin'
minio_secret_key = '12345678'
bucket_name = 'btc-prediction'
api_key = "RVMmqTn1fS3qfq35f4HA2z93T0NCIGHsrqqP9lvbb639Aor9OLw1h5B2hM6jWffq"
api_secret = "vTaHbz55Gn0z40Gwqt8ZCmDmWHnAWRNRHL6QjS0xpO6kTfDhgOSP9wvRU96wEM4g"

feature_names = [
      'Open', 'High', 'Low', 'Close', 'Volume',
      'Quote_asset_volume', 'Number_of_trades',
       'Taker_buy_base_asset_volume', 'Taker_buy_base_quote_volume', 
       'SMA', 'VWAP', 
       'DCdown', 'DCup', 'DCmid',
       'BollingerBasis', 'BollingerUpper', 'BollingerLower',
       'Past_trend_Open_2h', 
       'Past_trend_Open_3h', 
       'Past_trend_Open_2h_flag',
       'Past_trend_Open_3h_flag'
       ]
target_column = "target"

def process_input(data_frame, feature_cols, target_col="target"):
    print(data_frame[feature_cols].head(10))
    X_train = data_frame[feature_cols][3:-1]
    y_train = data_frame[target_col][3:-1]

    # Feature scaling
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)

    X_test = data_frame[feature_cols].tail(1)
    X_test = scaler.fit_transform(X_test)

    return X_train, y_train, X_test

def fit_and_predict(data_frame):

    X_train, y_train, X_test  = process_input(data_frame, feature_names, target_col="target")

    # Initialize and train the model
    model = RidgeCV(alphas=[0.1, 1.0, 10.0])
    model.fit(X_train, y_train)

    current_value = y_train.tail(1).tolist()[0]

    predict_value = float(model.predict(X_test)[0])
    return current_value, round(predict_value, 2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bitcoin Data Pipeline - Extract và Transform')
    parser.add_argument('--start-date', type=str, default="2025-10-16 09:00:00", help='Start date (e.g., "1 Jan, 2020" hoặc "2025-01-01")')
    parser.add_argument('--end-date', type=str, default="2025-10-17 11:00:00", help='Start date (e.g., "1 Jan, 2020" hoặc "2025-01-01")')
    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d %H:%M:%S")

    print("start_date 0 :", start_date)
    print("end_date 0 :", end_date)

    start_timestamp_ms = int(start_date.timestamp() * 1000)
    end_timestamp_ms = int(end_date.timestamp() * 1000)

    print("start_timestamp_ms :", start_timestamp_ms)
    print("end_timestamp_ms :", end_timestamp_ms)

    df = read_raw_data_from_minio(
        bucket_name=bucket_name,
        prefix="processed",
        start_date=start_timestamp_ms,
        end_date=end_timestamp_ms,
    )
    
    current_value, predict_value = fit_and_predict(df)
    
    one_hour_ms = 3600 * 1000  # 3600000
    
    # Lấy thời gian từ data cuối cùng trong dataframe
    last_open_time_ms = int(df['Open_time'].max())
    
    print(f"Last data point time: {last_open_time_ms} ({datetime.fromtimestamp(last_open_time_ms/1000)})")
    
    # Insert current_value (giá thực tế) tại thời điểm của data cuối cùng
    insert_data_postgres(
        time_value=last_open_time_ms/1000,  # Giá thực tế tại thời điểm data cuối
        price=current_value,
        trade_type="real"
    )

    # Insert predict_value (giá dự đoán) cho 1 giờ tiếp theo
    insert_data_postgres(
        time_value=(last_open_time_ms + one_hour_ms)/1000,  # Dự đoán cho data cuối + 1h
        price=predict_value,
        trade_type="predict"
    )
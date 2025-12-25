import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import argparse
import sys, os
import pickle
import boto3
from botocore.exceptions import ClientError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_pipeline.transform import read_raw_data_from_minio
from data_pipeline.load import insert_data_postgres

mode = 'full_pipeline'
minio_host = 'minio'
minio_port = 9000
minio_access_key = 'minio_user'
minio_secret_key = 'minio_password'
bucket_name = 'btc-prediction'
model_bucket_name = 'btc-prediction'
api_key = "RVMmqTn1fS3qfq35f4HA2z93T0NCIGHsrqqP9lvbb639Aor9OLw1h5B2hM6jWffq"
api_secret = "vTaHbz55Gn0z40Gwqt8ZCmDmWHnAWRNRHL6QjS0xpO6kTfDhgOSP9wvRU96wEM4g"

# Initialize boto3 S3 client for MinIO
s3_client = boto3.client(
    's3',
    endpoint_url=f'http://{minio_host}:{minio_port}',
    aws_access_key_id=minio_access_key,
    aws_secret_access_key=minio_secret_key,
    region_name='us-east-1',
    config=boto3.session.Config(signature_version='s3v4')
)

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
    """Process input data and split into train/test sets."""
    print(data_frame[feature_cols].head(10))
    X_train = data_frame[feature_cols][3:-1]
    y_train = data_frame[target_col][3:-1]

    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    X_test = data_frame[feature_cols].tail(1)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, y_train, X_test_scaled, scaler


def get_model_candidates():
    """Define model candidates with small grid search parameters for fast training."""
    models = {
        'Ridge': {
            'model': Ridge(),
            'params': {
                'alpha': [0.1, 1.0, 10.0]
            }
        },
        'Lasso': {
            'model': Lasso(),
            'params': {
                'alpha': [0.1, 1.0, 10.0]
            }
        },
        'ElasticNet': {
            'model': ElasticNet(),
            'params': {
                'alpha': [0.1, 1.0],
                'l1_ratio': [0.3, 0.7]
            }
        },
        'RandomForest': {
            'model': RandomForestRegressor(random_state=42),
            'params': {
                'n_estimators': [50, 100],
                'max_depth': [5, 10]
            }
        },
        'GradientBoosting': {
            'model': GradientBoostingRegressor(random_state=42),
            'params': {
                'n_estimators': [50, 100],
                'learning_rate': [0.1, 0.01],
                'max_depth': [3, 5]
            }
        }
    }
    return models


def train_models_with_gridsearch(X_train, y_train):
    """Train multiple models with GridSearchCV and return the best one."""
    models = get_model_candidates()
    best_model = None
    best_score = float('-inf')
    best_model_name = None
    results = {}
    
    print("\n" + "="*60)
    print("TRAINING MULTIPLE MODELS WITH GRIDSEARCH")
    print("="*60)
    
    for name, config in models.items():

        # scoring = rmse
        grid_search = GridSearchCV(
            estimator=config['model'],
            param_grid=config['params'],
            cv=3,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Get results
        mse_score = -grid_search.best_score_
        results[name] = {
            'best_params': grid_search.best_params_,
            'mse': mse_score,
            'rmse': mse_score ** 0.5,
            'model': grid_search.best_estimator_
        }
        
        # Track best model
        if -grid_search.best_score_ > best_score:
            best_score = -grid_search.best_score_
            best_model = grid_search.best_estimator_
            best_model_name = name
    
    return best_model, best_model_name, results


def save_model_to_s3(model, scaler, model_name, metrics, model_info):
    """Save model, scaler, and metadata to MinIO S3 using boto3."""
    try:
        # Create model package
        model_data = {
            'model': model,
            'scaler': scaler,
            'model_name': model_name,
            'metrics': metrics,
            'model_info': model_info,
            'timestamp': datetime.now().isoformat()
        }
        
        # Serialize to bytes
        model_bytes = pickle.dumps(model_data)
        
        # Upload to S3 using boto3
        object_name = f"models/{model_name}_challenger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        s3_client.put_object(
            Bucket=model_bucket_name,
            Key=object_name,
            Body=model_bytes
        )
        
        print(f"✅ Challenger model saved: {object_name}")
        return object_name
        
    except ClientError as e:
        print(f"❌ Error saving model to S3: {e}")
        return None


def load_champion_model_from_s3():
    """Load the current champion model from MinIO S3 using boto3."""
    try:
        champion_path = "models/champion_model.pkl"
        
        response = s3_client.get_object(
            Bucket=model_bucket_name,
            Key=champion_path
        )
        
        model_bytes = response['Body'].read()
        model_data = pickle.loads(model_bytes)
        
        print(f"✅ Champion model loaded: {model_data['model_name']}")
        print(f"   Metrics: {model_data['metrics']}")
        
        return model_data
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"⚠️  No champion model found")
        else:
            print(f"⚠️  Error loading champion: {e}")
        return None


def evaluate_model(model, X_test, y_test):
    """Evaluate model performance."""
    predictions = model.predict(X_test)
    
    mse = mean_squared_error(y_test, predictions)
    rmse = mse ** 0.5
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2': r2
    }


def champion_challenger_competition(challenger_model, challenger_name, X_train, y_train):    
    # Load champion model
    champion_data = load_champion_model_from_s3()
    
    # Evaluate challenger on validation data (last 20% of training data)
    split_idx = int(len(X_train) * 0.8)
    X_val = X_train[split_idx:]
    y_val = y_train.iloc[split_idx:]
    
    challenger_metrics = evaluate_model(challenger_model, X_val, y_val)
    
    # If no champion, challenger becomes champion
    if champion_data is None:
        print("\n⚠️  No champion found. Challenger becomes champion!")
        return challenger_model, challenger_name, challenger_metrics, True
    
    # Evaluate champion
    champion_model = champion_data['model']
    champion_metrics = evaluate_model(champion_model, X_val, y_val)
    
    # Compare performance (lower RMSE is better)
    if challenger_metrics['rmse'] < champion_metrics['rmse']:
        improvement = ((champion_metrics['rmse'] - challenger_metrics['rmse']) / champion_metrics['rmse']) * 100
        print(f"\n🎉 CHALLENGER WINS! Improvement: {improvement:.2f}%")
        print("="*60 + "\n")
        return challenger_model, challenger_name, challenger_metrics, True
    else:
        print(f"\n🛡️  CHAMPION RETAINS TITLE!")
        print("="*60 + "\n")
        return champion_model, champion_data['model_name'], champion_metrics, False


def promote_to_champion(model, scaler, model_name, metrics):
    """Promote a model to champion status using boto3."""
    try:
        model_data = {
            'model': model,
            'scaler': scaler,
            'model_name': model_name,
            'metrics': metrics,
            'promoted_at': datetime.now().isoformat()
        }
        
        model_bytes = pickle.dumps(model_data)
        
        # Save as champion using boto3
        s3_client.put_object(
            Bucket=model_bucket_name,
            Key="models/champion_model.pkl",
            Body=model_bytes
        )
        
        print(f"✅ Model promoted to CHAMPION: {model_name}")
        print(f"   RMSE: {metrics['rmse']:.4f}")
        print(f"   MAE: {metrics['mae']:.4f}")
        print(f"   R²: {metrics['r2']:.4f}")
        
    except ClientError as e:
        print(f"❌ Error promoting model: {e}")


def fit_and_predict(data_frame):
    """Main training and prediction function with champion-challenger pattern."""    
    X_train, y_train, X_test, scaler = process_input(data_frame, feature_names, target_col="target")

    # Train multiple models with GridSearchCV
    best_model, best_model_name, all_results = train_models_with_gridsearch(X_train, y_train)
    
    # Save challenger model
    save_model_to_s3(
        model=best_model,
        scaler=scaler,
        model_name=best_model_name,
        metrics=all_results[best_model_name],
        model_info=all_results
    )
    
    # Champion-Challenger competition
    winning_model, winning_name, winning_metrics, is_new_champion = champion_challenger_competition(
        best_model, best_model_name, X_train, y_train
    )
    
    # Promote to champion if challenger won
    if is_new_champion:
        promote_to_champion(winning_model, scaler, winning_name, winning_metrics)
    
    # Make prediction
    current_value = y_train.iloc[-1]
    predict_value = float(winning_model.predict(X_test)[0])
    
    print(f"\n📊 Prediction Results:")
    print(f"   Current Value: {current_value:.2f}")
    print(f"   Predicted Value: {predict_value:.2f}")
    print(f"   Model Used: {winning_name}\n")
    
    return current_value, round(predict_value, 2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bitcoin Data Pipeline - Extract và Transform')
    parser.add_argument('--end-date', type=str, default=None, help='End date (e.g., "2025-10-17 11:00:00"). Default: now')
    args = parser.parse_args()

    # Always use 30 days timeframe
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d %H:%M:%S")
    else:
        end_date = datetime.now()
    
    # Always calculate start_date as 30 days before end_date
    start_date = end_date - timedelta(days=30)

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
    df = df.fillna(method='ffill')
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
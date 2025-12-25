# Architecture Overview

## 📐 System Architecture

Dự án BTC Prediction MLOps được thiết kế theo kiến trúc microservices với các thành phần độc lập, dễ dàng mở rộng và bảo trì.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Services                         │
├─────────────────────────────────────────────────────────────────┤
│                         Binance API                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Ingestion Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐     ┌──────────────┐  │
│  │   Extract    │─────▶│  Transform   │────▶│     Load     │  │
│  │  (Binance)   │      │  (Features)  │     │ (MinIO/PG)   │  │
│  └──────────────┘      └──────────────┘     └──────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐     ┌──────────────┐  │
│  │    MinIO     │      │ PostgreSQL   │     │   MinIO      │  │
│  │  (Raw Data)  │      │  (Metadata)  │     │   (Models)   │  │
│  └──────────────┘      └──────────────┘     └──────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ML Training Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐     ┌──────────────┐  │
│  │Feature Eng.  │─────▶│Model Training│────▶│   Evaluate   │  │
│  │  (Pipeline)  │      │(Grid Search) │     │(Best Model)  │  │
│  └──────────────┘      └──────────────┘     └──────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Prediction Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐     ┌──────────────┐  │
│  │ Load Model   │─────▶│   Predict    │────▶│Store Results │  │
│  │ (From MinIO) │      │(BTC Price)   │     │(PostgreSQL)  │  │
│  └──────────────┘      └──────────────┘     └──────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                             │
├─────────────────────────────────────────────────────────────────┤
│              Apache Airflow (Scheduler + DAGs)                   │
└─────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CI/CD Layer                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐     ┌──────────────┐  │
│  │    Gitea     │─────▶│   Jenkins    │────▶│Deploy/Test   │  │
│  │(Git Server)  │      │(Build/Test)  │     │(Automation)  │  │
│  └──────────────┘      └──────────────┘     └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Data Ingestion Layer

**Purpose**: Thu thập và xử lý dữ liệu Bitcoin từ Binance API

**Components**:
- **Extract Module** (`data_pipeline/extract.py`):
  - Kết nối với Binance API
  - Thu thập OHLCV data (Open, High, Low, Close, Volume)
  - Hỗ trợ khoảng thời gian tùy chỉnh
  - Xử lý rate limiting và retry logic

- **Transform Module** (`data_pipeline/transform.py`):
  - Feature engineering (SMA, VWAP, Bollinger Bands)
  - Data quality checks
  - Data profiling với ydata_profiling
  - Normalization và scaling

- **Load Module** (`data_pipeline/load.py`):
  - Lưu raw data lên MinIO (partitioned by date)
  - Lưu processed data lên MinIO
  - Insert predictions vào PostgreSQL
  - Error handling và logging

### 2. Storage Layer

**MinIO (S3-Compatible Storage)**:
- **Raw Data Bucket**: `btc-prediction/raw/`
  - Parquet files partitioned by year/month/day
  - Immutable raw data
- **Processed Data Bucket**: `btc-prediction/processed/`
  - Feature-engineered data
  - Ready for model training
- **Model Bucket**: `btc-prediction/models/`
  - Serialized model files (.pkl)
  - Model metadata and versioning

**PostgreSQL**:
- **Airflow Metadata**: DAG runs, task instances, logs
- **Predictions Table**: Lưu trữ kết quả dự đoán
- **Model Performance**: Metrics và evaluation results

### 3. ML Training Layer

**Components**:

- **Model Training** (`btc_prediction/train_and_predict.py`):
  - Multiple model support:
    - Ridge Regression
    - Lasso Regression
    - ElasticNet
    - Random Forest
    - Gradient Boosting
  - Grid Search for hyperparameter tuning
  - Cross-validation
  - Model serialization

- **Model Evaluation**:
  - MSE (Mean Squared Error)
  - MAE (Mean Absolute Error)
  - R² Score
  - Model comparison và selection

### 4. Prediction Layer

**Components**:

- **Model Loading** (`btc_prediction/train_and_predict.py`):
  - Load best model từ MinIO
  - Load scaler và preprocessing artifacts

- **Prediction Service**:
  - Real-time predictions
  - Batch predictions
  - Feature preprocessing
  - Result formatting

- **Result Storage**:
  - Save predictions to PostgreSQL
  - Timestamp và metadata tracking
  - Version control

### 5. Orchestration Layer

**Apache Airflow**:

- **DAG Definition** (`dags/etl_and_predict_btc.py`):
  - Schedule: Hourly (`0 * * * *`)
  - Tasks:
    1. `run_etl_pipeline`: Extract, Transform, Load
    2. `run_train_model`: Train và predict
  - Dependencies: ETL → Training

- **Features**:
  - Task retry mechanism
  - Email notifications on failure
  - Task logging và monitoring
  - Backfill support

### 6. CI/CD Layer

**Jenkins**:
- Automated testing (pytest)
- Code quality checks (ruff, pylint)
- Docker image building
- Deployment automation

**Gitea**:
- Git repository hosting
- Webhook integration với Jenkins
- Pull request workflows

## 🔄 Data Flow

### ETL Pipeline Flow

```
1. Binance API Call
   ├─ Get OHLCV data for time range
   └─ Handle pagination

2. Data Extraction
   ├─ Fetch hourly candles
   ├─ Validate data completeness
   └─ Save to MinIO (raw)

3. Data Transformation
   ├─ Calculate technical indicators
   ├─ Generate features
   ├─ Data quality checks
   └─ Save to MinIO (processed)

4. Data Loading
   ├─ Load to PostgreSQL (if needed)
   └─ Update metadata tables
```

### ML Training Flow

```
1. Data Loading
   ├─ Read processed data from MinIO
   └─ Filter by date range

2. Feature Preparation
   ├─ Select feature columns
   ├─ Split train/test
   └─ Scale features (StandardScaler)

3. Model Training
   ├─ For each model candidate:
   │   ├─ Grid search hyperparameters
   │   ├─ Train với best params
   │   └─ Evaluate performance
   └─ Select best model

4. Model Saving
   ├─ Serialize model + scaler
   ├─ Save to MinIO
   └─ Log metrics to database

5. Prediction
   ├─ Load latest features
   ├─ Predict next hour price
   └─ Save to PostgreSQL
```

## 🔐 Security Architecture

### Authentication & Authorization

- **MinIO**: Access key + Secret key authentication
- **PostgreSQL**: Username/password authentication
- **Airflow**: Web authentication (admin/admin)
- **Jenkins**: User-based authentication
- **Gitea**: User accounts with SSH keys

### Network Security

- All services run in Docker network
- Exposed ports:
  - Airflow: 8080
  - Jenkins: 8081
  - Gitea: 3001
  - MinIO Console: 9001
  - PostgreSQL: 5432 (internal)

### Data Security

- Secrets managed via environment variables
- No hardcoded credentials
- API keys stored in `.env` file (not in git)
- TLS/SSL for external API calls

## 📊 Monitoring & Logging

### Logging Strategy

- **Application Logs**: Using `loguru` library
  - Structured logging
  - Log levels: DEBUG, INFO, WARNING, ERROR
  - Log rotation và archival

- **Airflow Logs**: 
  - Task execution logs
  - Scheduler logs
  - Stored in `/opt/airflow/logs/`

- **Docker Logs**:
  - `docker-compose logs <service>`
  - Persisted trong container volumes

### Monitoring Points

- **Data Quality**: Profiling reports
- **Model Performance**: MSE, MAE, R² metrics
- **Pipeline Health**: Airflow task success rate
- **Resource Usage**: Docker container stats
- **API Health**: Binance API response time

## 🚀 Scalability Considerations

### Horizontal Scaling

- **Airflow**: Add more worker nodes
- **MinIO**: Distributed mode với multiple nodes
- **PostgreSQL**: Read replicas for queries

### Vertical Scaling

- Increase Docker container resources
- Optimize model training parameters
- Database query optimization

### Performance Optimization

- Batch processing for large datasets
- Caching frequently accessed data
- Parallel model training
- Incremental data loading

## 🔧 Configuration Management

### Environment Variables

All configurations stored in `.env`:
- Database connections
- API credentials
- Service endpoints
- Feature flags

## 📈 Future Architecture Enhancements

### Planned Improvements

1. **Model Serving**:
   - FastAPI/Flask REST API for predictions
   - Model serving với MLflow
   - A/B testing infrastructure

2. **Real-time Processing**:
   - Kafka/Redis for streaming data
   - Real-time feature computation
   - Online learning capabilities

3. **Advanced Monitoring**:
   - Prometheus + Grafana dashboards
   - Model drift detection
   - Data drift monitoring
   - Alerting system

4. **Enhanced Security**:
   - HashiCorp Vault for secrets
   - RBAC (Role-Based Access Control)
   - Audit logging
   - Encryption at rest

5. **Scalability**:
   - Kubernetes deployment
   - Auto-scaling policies
   - Load balancing
   - Multi-region support

## 📚 Related Documentation

- [Data Pipeline Details](data-pipeline.md)
- [ML Pipeline Details](ml-pipeline.md)
- [Deployment Guide](../deployment/docker.md)
- [API Reference](../api/data-pipeline.md)

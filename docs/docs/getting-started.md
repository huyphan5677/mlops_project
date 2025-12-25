# Getting Started

Hướng dẫn chi tiết để setup và chạy dự án BTC Prediction MLOps.

## 📋 Prerequisites

Trước khi bắt đầu, đảm bảo bạn đã cài đặt:

- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **Docker & Docker Compose**: [Install Docker](https://docs.docker.com/get-docker/)
- **Git**: [Install Git](https://git-scm.com/downloads)
- **Make** (Optional): Để sử dụng Makefile commands

### Kiểm tra cài đặt

```bash
python --version  # Should be 3.10+
docker --version
docker-compose --version
git --version
```

## 🔧 Installation

### 1. Clone Repository

```bash
git clone https://github.com/huyphan5677/mlops_project.git
cd mlops_project
```

### 2. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install package in editable mode
pip install -e .

# Or install from requirements (if exists)
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Tạo file `.env` ở root directory:

```bash
# MinIO Configuration
MINIO_HOST=minio
MINIO_PORT=9000
MINIO_ACCESS_KEY=minio_user
MINIO_SECRET_KEY=minio_password
MINIO_BUCKET=btc-prediction

# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=airflow_metadata
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow

# Binance API (Optional - for live data)
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Airflow Configuration
AIRFLOW_HOME=/opt/airflow
AIRFLOW__CORE__LOAD_EXAMPLES=False
```

## 🐳 Docker Setup

### 1. Start All Services

```bash
# Start all services
docker-compose up -d

# Check services status
docker-compose ps
```

### 2. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airflow** | http://localhost:8080 | admin / admin |
| **Jenkins** | http://localhost:8081/jenkins/ | admin / (check logs) |
| **Gitea** | http://localhost:3001 | gitea / gitea123 |
| **MinIO Console** | http://localhost:9001 | minio_user / minio_password |

### 3. Get Jenkins Password

```bash
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 4. Create Gitea Database

```bash
docker exec -it airflow_postgres psql -U airflow -d airflow_metadata -c "CREATE DATABASE gitea;"
```

## 🚀 Running Your First Pipeline

### Option 1: Manual Run

#### Step 1: Run ETL Pipeline

```bash
# Extract, transform, load Bitcoin data
python data_pipeline/pipeline.py \
    --start-date "2025-01-01 00:00:00" \
    --end-date "2025-01-02 00:00:00"
```

**Parameters:**
- `--start-date`: Ngày bắt đầu lấy dữ liệu (format: YYYY-MM-DD HH:MM:SS)
- `--end-date`: Ngày kết thúc lấy dữ liệu

**Output:**
- Raw data saved to MinIO: `s3://btc-prediction/raw/`
- Processed data saved to MinIO: `s3://btc-prediction/processed/`
- Data quality report: `/opt/airflow/logs/profiling/`

#### Step 2: Train Model

```bash
# Train and predict with multiple models
python btc_prediction/train_and_predict.py \
    --end-date "2025-01-02 00:00:00"
```

**Output:**
- Best model saved to MinIO: `s3://btc-prediction/models/`
- Predictions saved to PostgreSQL
- Model metrics logged

### Option 2: Using Airflow

1. **Access Airflow UI**: http://localhost:8080
2. **Enable DAG**: Tìm `daily_etl_train_dag` và enable
3. **Trigger DAG**: Click nút play để chạy manual
4. **Monitor**: Xem logs và status của từng task

### Option 3: Using Make

```bash
# Run tests
make test

# Run with coverage
make test-coverage

# Clean build artifacts
make clean
```

## 📊 Verify Installation

### 1. Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=./ --cov-report=term-missing

# Run specific test module
pytest tests/btc_prediction/test_train.py
pytest tests/data_pipeline/test_extract.py
```

### 2. Check MinIO Data

```bash
# List buckets
docker exec -it minio mc ls minio/

# List files in bucket
docker exec -it minio mc ls minio/btc-prediction/
```

### 3. Check PostgreSQL Data

```bash
# Connect to PostgreSQL
docker exec -it airflow_postgres psql -U airflow -d airflow_metadata

# Query predictions table
SELECT * FROM btc_predictions ORDER BY prediction_time DESC LIMIT 10;
```

## 🔍 Troubleshooting

### Issue: Port already in use

```bash
# Check what's using the port
netstat -ano | findstr :8080
netstat -ano | findstr :9000

# Kill the process or change port in docker-compose.yml
```

### Issue: Docker services not starting

```bash
# Check logs
docker-compose logs <service_name>

# Restart specific service
docker-compose restart <service_name>

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Issue: Python module not found

```bash
# Reinstall in editable mode
pip install -e .

# Or install specific package
pip install <package_name>
```

### Issue: MinIO connection error

```bash
# Check MinIO is running
docker ps | grep minio

# Verify credentials in .env file
# Restart MinIO
docker-compose restart minio
```

### Issue: Airflow DAG not showing

```bash
# Check Airflow logs
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver

# Refresh DAG
docker exec -it airflow-scheduler airflow dags list
```

## 📚 Next Steps

Sau khi setup thành công, bạn có thể:

1. **Khám phá Architecture**: Xem [Architecture Overview](architecture/overview.md)
2. **Tùy chỉnh Configuration**: Đọc [Configuration Guide](guide/configuration.md)
3. **Training Models**: Xem [Model Training Guide](guide/model-training.md)
4. **Setup CI/CD**: Theo dõi [CI/CD Guide](development/cicd.md)
5. **Deploy to Production**: Xem [Deployment Guide](deployment/docker.md)

## 💡 Tips

- Sử dụng `docker-compose logs -f <service>` để xem logs real-time
- Backup MinIO data thường xuyên
- Monitor Airflow scheduler health
- Keep dependencies updated
- Use virtual environment cho development

## 🆘 Need Help?

- Check [Documentation](index.md)
- Open an [Issue](https://github.com/huyphan5677/mlops_project/issues)
- Read [API Reference](api/data-pipeline.md)

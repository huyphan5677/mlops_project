# BTC Prediction MLOps Project

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Overview

Dự án **BTC Prediction MLOps** là một hệ thống end-to-end machine learning pipeline để dự đoán giá Bitcoin. Dự án được xây dựng theo chuẩn **Cookiecutter Data Science** và tích hợp đầy đủ các công cụ MLOps hiện đại.

## ✨ Key Features

- 🔄 **Automated ETL Pipeline**: Thu thập và xử lý dữ liệu Bitcoin từ Binance API theo thời gian thực
- 🤖 **ML Model Training**: Huấn luyện và so sánh nhiều mô hình (Ridge, Lasso, RandomForest, GradientBoosting)
- 📊 **Data Profiling**: Tự động kiểm tra chất lượng dữ liệu
- 🚀 **CI/CD Integration**: Jenkins + Gitea cho continuous integration
- 📦 **Model Versioning**: Lưu trữ models trên MinIO S3-compatible storage
- ⏰ **Scheduled Workflows**: Airflow DAGs để chạy pipeline tự động
- 🐳 **Containerized**: Đầy đủ Docker setup cho development và production
- 🧪 **Testing**: Comprehensive test suite với pytest

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Binance   │────▶│  ETL Pipeline│────▶│   MinIO     │
│     API     │     │   (Airflow)  │     │  (Storage)  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  PostgreSQL  │     │  ML Pipeline│
                    │  (Metadata)  │     │  (Training) │
                    └──────────────┘     └─────────────┘
                                                 │
                                                 ▼
                                        ┌─────────────┐
                                        │  Prediction │
                                        │   Service   │
                                        └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Make (optional)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd mlops_project

# Install dependencies
pip install -e .

# Or using make
make install
```

### Running the Pipeline

```bash
# Run ETL pipeline
python data_pipeline/pipeline.py --start-date "2025-01-01 00:00:00" --end-date "2025-01-02 00:00:00"

# Train model
python btc_prediction/train_and_predict.py --end-date "2025-01-02 00:00:00"
```

### Using Docker

```bash
# Start all services
docker-compose up -d

# Access services
# Airflow: http://localhost:8080
# Jenkins: http://localhost:8081/jenkins/
# Gitea: http://localhost:3001
# MinIO: http://localhost:9001
```

## 📁 Project Structure

```
mlops_project/
├── btc_prediction/         # ML model training and prediction
│   └── train_and_predict.py # Main training script
├── data_pipeline/          # ETL pipeline
│   ├── extract.py          # Data extraction from Binance
│   ├── transform.py        # Data transformation
│   ├── load.py             # Data loading to PostgreSQL
│   └── pipeline.py         # Orchestration
├── dags/                   # Airflow DAGs
│   └── etl_and_predict_btc.py
├── tests/                  # Test suite
├── docs/                   # Documentation (MkDocs)
├── notebooks/              # Jupyter notebooks
├── reports/                # Generated reports
└── references/             # Reference materials
```

## 🛠️ Technology Stack

- **ML Framework**: scikit-learn
- **Data Processing**: pandas, numpy
- **Workflow**: Apache Airflow
- **Storage**: MinIO (S3-compatible), PostgreSQL
- **CI/CD**: Jenkins, Gitea
- **Testing**: pytest
- **Documentation**: MkDocs
- **Containerization**: Docker

## 📊 Model Performance

Dự án hỗ trợ nhiều loại model:
- Ridge Regression
- Lasso Regression
- ElasticNet
- Random Forest Regressor
- Gradient Boosting Regressor

Model được đánh giá dựa trên các metrics:
- Mean Squared Error (MSE)
- Mean Absolute Error (MAE)
- R² Score

## 📖 Documentation

Xem [Getting Started](getting-started.md) để bắt đầu hoặc khám phá các phần khác:

- [Architecture Overview](architecture/overview.md)
- [Data Pipeline Guide](architecture/data-pipeline.md)
- [Model Training Guide](guide/model-training.md)
- [API Reference](api/data-pipeline.md)
- [Development Setup](development/setup.md)
- [Testing Guide](development/testing.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=./ --cov-report=term-missing

# Run specific test suite
pytest tests/btc_prediction/
pytest tests/data_pipeline/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

MLOps Team

## 🔗 Links

- [Project Repository](https://github.com/huyphan5677/mlops_project)
- [Issue Tracker](https://github.com/huyphan5677/mlops_project/issues)

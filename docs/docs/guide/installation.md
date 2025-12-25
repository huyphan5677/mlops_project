# Installation Guide

## 📋 System Requirements

### Hardware Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB free space
- Network: Stable internet connection

**Recommended**:
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB SSD
- Network: High-speed connection

### Software Requirements

- **Operating System**:
  - Windows 10/11 (64-bit)
  - macOS 10.15+
  - Linux (Ubuntu 20.04+, CentOS 8+)

- **Python**: Version 3.10 or higher
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: Latest stable version

## 🔧 Step-by-Step Installation

### Step 1: Install Python

#### Windows

```powershell
# Download from python.org
# Or use Chocolatey
choco install python --version=3.10

# Verify installation
python --version
```

#### macOS

```bash
# Using Homebrew
brew install python@3.10

# Verify installation
python3 --version
```

#### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip

# Verify installation
python3.10 --version
```

### Step 2: Install Docker

#### Windows

1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Run installer
3. Restart computer
4. Start Docker Desktop
5. Verify:
   ```powershell
   docker --version
   docker-compose --version
   ```

#### macOS

```bash
# Using Homebrew
brew install --cask docker

# Or download from docker.com
# Start Docker Desktop from Applications

# Verify
docker --version
docker-compose --version
```

#### Linux (Ubuntu)

```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

### Step 3: Install Git

#### Windows

```powershell
# Using Chocolatey
choco install git

# Or download from git-scm.com
# Verify
git --version
```

#### macOS

```bash
# Using Homebrew
brew install git

# Verify
git --version
```

#### Linux

```bash
sudo apt install git

# Verify
git --version
```

### Step 4: Clone Repository

```bash
# Clone the project
git clone https://github.com/huyphan5677/mlops_project.git

# Navigate to project directory
cd mlops_project

# Check project structure
ls -la
```

### Step 5: Setup Python Environment

#### Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
.\venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate

# Verify activation
which python  # Should show venv path
```

#### Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project in editable mode
pip install -e .

# Verify installation
pip list | grep btc-prediction
```

### Step 6: Setup Environment Variables

#### Create .env File

```bash
# Create .env file
touch .env  # Linux/macOS
type nul > .env  # Windows

# Or copy from template
cp .env.example .env  # If exists
```

#### Configure .env

Edit `.env` file:

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

# Binance API (Optional)
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Airflow Configuration
AIRFLOW_HOME=/opt/airflow
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__WEBSERVER__SECRET_KEY=changeme

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

### Step 7: Initialize Docker Services

#### Pull Docker Images

```bash
# Pull all required images
docker-compose pull

# This will download:
# - apache/airflow:2.x
# - postgres:13
# - minio/minio
# - jenkins/jenkins
# - gitea/gitea
```

#### Initialize Airflow Database

```bash
# Initialize Airflow metadata DB
docker-compose run --rm airflow-init
```

#### Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 8: Verify Installation

#### Check Services

```bash
# Check running containers
docker ps

# Expected output:
# - airflow-webserver
# - airflow-scheduler
# - airflow-postgres
# - minio
# - jenkins
# - gitea
```

#### Access Web Interfaces

Open browser and navigate to:

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Airflow | http://localhost:8080 | admin / admin |
| Jenkins | http://localhost:8081/jenkins/ | admin / (see logs) |
| Gitea | http://localhost:3001 | gitea / gitea123 |
| MinIO | http://localhost:9001 | minio_user / minio_password |

#### Run Health Checks

```bash
# Check Airflow
docker exec -it airflow-webserver airflow db check

# Check PostgreSQL
docker exec -it airflow-postgres pg_isready -U airflow

# Check MinIO
docker exec -it minio mc alias set minio http://localhost:9000 minio_user minio_password

# Check Jenkins
curl http://localhost:8081/jenkins/login
```

### Step 9: Setup Additional Services

#### Get Jenkins Initial Password

```bash
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Copy the password and use it to unlock Jenkins at first login.

#### Create Gitea Database

```bash
docker exec -it airflow-postgres psql -U airflow -d airflow_metadata -c "CREATE DATABASE gitea;"
```

#### Setup MinIO Buckets

```bash
# Access MinIO console: http://localhost:9001
# Login with credentials
# Create bucket: btc-prediction

# Or use CLI
docker exec -it minio mc mb minio/btc-prediction
```

### Step 10: Run Tests

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate  # Windows

# Run all tests
pytest

# Run with coverage
pytest --cov=./ --cov-report=term-missing

# Expected: All tests should pass
```

### Step 11: Run First Pipeline

```bash
# Run ETL pipeline
python data_pipeline/pipeline.py \
    --start-date "2025-01-01 00:00:00" \
    --end-date "2025-01-02 00:00:00"

# Expected output:
# - Data extracted from Binance
# - Features generated
# - Data saved to MinIO
# - Profiling reports created

# Run model training
python btc_prediction/train_and_predict.py \
    --end-date "2025-01-02 00:00:00"

# Expected output:
# - Models trained
# - Best model selected
# - Prediction made
# - Results saved
```

## 🔧 Advanced Configuration

### Docker Memory Allocation

```bash
# Check Docker resource limits
docker info | grep Memory

# Adjust in Docker Desktop Settings:
# - Windows/macOS: Preferences → Resources
# - Recommended: 4GB+ for smooth operation
```

### Python Package Development Install

```bash
# Install in development mode with extras
pip install -e ".[dev]"

# This installs additional dev dependencies:
# - pytest
# - pytest-cov
# - ruff
# - pylint
```

### Custom Docker Compose

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'

services:
  airflow-webserver:
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/opt/airflow/logs
  
  minio:
    environment:
      - MINIO_BROWSER_REDIRECT_URL=http://localhost:9001
```

## 🚨 Troubleshooting

### Python Version Issues

```bash
# If multiple Python versions installed
python3.10 -m venv venv

# Or use pyenv
pyenv install 3.10.0
pyenv local 3.10.0
```

### Docker Permission Denied (Linux)

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
# Or use newgrp
newgrp docker

# Verify
docker run hello-world
```

### Port Already in Use

```bash
# Find process using port
# Linux/macOS
lsof -i :8080

# Windows
netstat -ano | findstr :8080

# Kill process or change port in docker-compose.yml
```

### MinIO Connection Failed

```bash
# Check MinIO is running
docker ps | grep minio

# Check logs
docker logs minio

# Restart service
docker-compose restart minio
```

### Airflow Webserver Not Starting

```bash
# Check logs
docker logs airflow-webserver

# Reinitialize database
docker-compose down -v
docker-compose run --rm airflow-init
docker-compose up -d
```

### Package Installation Fails

```bash
# Update pip
pip install --upgrade pip setuptools wheel

# Clear cache
pip cache purge

# Retry installation
pip install -e .
```

## 🔄 Updating Installation

### Update Docker Images

```bash
# Pull latest images
docker-compose pull

# Recreate containers
docker-compose up -d --force-recreate
```

### Update Python Packages

```bash
# Activate venv
source venv/bin/activate

# Update all packages
pip install --upgrade -e .

# Or update specific package
pip install --upgrade <package_name>
```

### Update Code

```bash
# Pull latest changes
git pull origin master

# Reinstall if dependencies changed
pip install -e .

# Restart services
docker-compose restart
```

## 📚 Next Steps

After successful installation:

1. ✅ [Getting Started Guide](../getting-started.md) - Run your first pipeline
2. ✅ [Configuration Guide](configuration.md) - Customize settings
3. ✅ [Running Pipeline](running-pipeline.md) - Learn pipeline operations
4. ✅ [Development Setup](../development/setup.md) - Setup for development

## 🆘 Need Help?

- Check [Troubleshooting Guide](../getting-started.md#troubleshooting)
- Open an [Issue](https://github.com/huyphan5677/mlops_project/issues)
- Read [Documentation](../index.md)

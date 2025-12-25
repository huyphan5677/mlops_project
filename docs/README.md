# BTC Prediction MLOps Documentation

Comprehensive documentation cho dự án Bitcoin Price Prediction MLOps.

## 📚 Documentation Structure

```
docs/
├── mkdocs.yml              # MkDocs configuration
├── README.md               # This file
└── docs/                   # Documentation content
    ├── index.md            # Homepage
    ├── getting-started.md  # Quick start guide
    ├── architecture/       # System architecture
    │   ├── overview.md
    │   ├── data-pipeline.md
    │   └── ml-pipeline.md
    ├── guide/              # User guides
    │   ├── installation.md
    │   ├── configuration.md
    │   ├── running-pipeline.md
    │   └── model-training.md
    ├── api/                # API reference
    │   ├── data-pipeline.md
    │   ├── btc-prediction.md
    │   └── models.md
    ├── development/        # Development guides
    │   ├── setup.md
    │   ├── testing.md
    │   └── cicd.md
    └── deployment/         # Deployment guides
        ├── docker.md
        ├── airflow.md
        └── monitoring.md
```

## 🚀 Generating the Docs

### Prerequisites

```bash
# Install MkDocs and dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]
```

### Build Documentation

Build locally with:

    mkdocs build

Serve locally with:

    mkdocs serve

Access at: http://127.0.0.1:8000

### Deploy Documentation

Deploy to GitHub Pages:

    mkdocs gh-deploy

## 📖 Documentation Sections

### 1. Getting Started
- **Purpose**: Quick start guide cho new users
- **Content**: Installation, first run, basic usage
- **Audience**: Beginners

### 2. Architecture
- **Purpose**: System design and data flow
- **Content**: 
  - Overall architecture
  - Data pipeline details
  - ML pipeline details
- **Audience**: Developers, architects

### 3. User Guide
- **Purpose**: Detailed how-to guides
- **Content**:
  - Installation steps
  - Configuration options
  - Running pipelines
  - Model training
- **Audience**: Users, operators

### 4. API Reference
- **Purpose**: Code-level documentation
- **Content**:
  - Function signatures
  - Class definitions
  - Module descriptions
- **Audience**: Developers

### 5. Development
- **Purpose**: Contributing and development setup
- **Content**:
  - Development environment
  - Testing guidelines
  - CI/CD setup
- **Audience**: Contributors

### 6. Deployment
- **Purpose**: Production deployment guides
- **Content**:
  - Docker deployment
  - Airflow setup
  - Monitoring setup
- **Audience**: DevOps, SRE

## ✍️ Contributing to Documentation

### Writing Guidelines

1. **Use clear, concise language**
2. **Include code examples**
3. **Add diagrams where helpful**
4. **Keep formatting consistent**
5. **Test all commands before documenting**

### Adding New Pages

1. Create new `.md` file in appropriate directory
2. Add entry to `mkdocs.yml` navigation
3. Write content following guidelines
4. Test locally with `mkdocs serve`
5. Submit pull request

## 📧 Contact

For documentation issues or suggestions:
- Open an [Issue](https://github.com/huyphan5677/mlops_project/issues)
- Submit a [Pull Request](https://github.com/huyphan5677/mlops_project/pulls)

---

Use [mkdocs](http://www.mkdocs.org/) structure to update the documentation.
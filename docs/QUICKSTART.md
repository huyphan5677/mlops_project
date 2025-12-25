# Quick Start: Building Documentation

## 🚀 Fast Track

```bash
# 1. Install dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# 2. Navigate to docs directory
cd docs

# 3. Serve documentation locally
mkdocs serve

# 4. Open browser
# Visit: http://127.0.0.1:8000
```

## 📖 What You Get

Sau khi chạy `mkdocs serve`, bạn có thể truy cập documentation với:

- ✅ **Live reload**: Tự động refresh khi bạn chỉnh sửa
- ✅ **Search functionality**: Tìm kiếm trong toàn bộ docs
- ✅ **Navigation**: Menu điều hướng rõ ràng
- ✅ **Code highlighting**: Syntax highlighting cho code blocks
- ✅ **Responsive design**: Hoạt động tốt trên mobile

## 📁 Documentation Structure

```
docs/
├── index.md                    # 🏠 Homepage
├── getting-started.md          # 🚀 Quick start guide
├── architecture/
│   ├── overview.md             # 📐 System architecture
│   ├── data-pipeline.md        # 📊 Data pipeline details
│   └── ml-pipeline.md          # 🤖 ML pipeline details
├── guide/
│   ├── installation.md         # 🔧 Installation guide
│   ├── configuration.md        # ⚙️ Configuration guide
│   ├── running-pipeline.md     # ▶️ Running pipelines
│   └── model-training.md       # 🎓 Model training
├── api/
│   ├── data-pipeline.md        # 📚 Data pipeline API
│   ├── btc-prediction.md       # 📚 ML API
│   └── models.md               # 📚 Models API
├── development/
│   ├── setup.md                # 💻 Dev setup
│   ├── testing.md              # 🧪 Testing guide
│   └── cicd.md                 # 🔄 CI/CD setup
└── deployment/
    ├── docker.md               # 🐳 Docker deployment
    ├── airflow.md              # ⏰ Airflow setup
    └── monitoring.md           # 📈 Monitoring
```

## 🎨 Key Features

### 1. Homepage (index.md)
- Project overview
- Key features
- Architecture diagram
- Quick start links
- Technology stack

### 2. Getting Started
- Prerequisites
- Installation steps
- First pipeline run
- Verification steps
- Troubleshooting

### 3. Architecture Documentation
- High-level system design
- Data flow diagrams
- Component interactions
- Technology decisions

### 4. User Guides
- Step-by-step tutorials
- Configuration options
- Best practices
- Common use cases

### 5. API Reference
- Function signatures
- Parameter descriptions
- Return values
- Code examples

### 6. Development Guides
- Development environment setup
- Testing strategies
- CI/CD pipelines
- Contributing guidelines

### 7. Deployment Guides
- Docker setup
- Airflow configuration
- Monitoring and logging
- Production best practices

## 🛠️ Building for Production

### Build Static Site

```bash
cd docs
mkdocs build
```

Output in `site/` directory - ready to deploy!

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

### Custom Domain

Add `CNAME` file to `docs/` directory:

```
your-domain.com
```

## 📝 Editing Documentation

### Edit Existing Pages

1. Open `.md` file in `docs/docs/` directory
2. Make changes
3. Save file
4. View changes at http://127.0.0.1:8000 (auto-reloads)

### Add New Page

1. Create new `.md` file in appropriate directory
2. Add to `mkdocs.yml`:

```yaml
nav:
  - Your Section:
      - New Page: section/new-page.md
```

3. Write content using Markdown
4. Test locally with `mkdocs serve`

## 🎯 Quick Tips

1. **Use clear headings**: H1 for page title, H2 for sections
2. **Include code examples**: Show, don't just tell
3. **Add diagrams**: Use Mermaid or ASCII diagrams
4. **Test all commands**: Verify before documenting
5. **Keep it updated**: Documentation is never "done"

## 🔗 Useful Links

- [Full Documentation README](../README.md)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)

---

**Happy documenting! 📚**

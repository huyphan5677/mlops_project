## Unitest (pytest)
```bash
pytest --cov=./ --cov-report=term-missing
# pytest tests/ --cov=./
```

## Jenkins + Gitea
- Jenkins: http://localhost:8081/jenkins/ (user: `admin` and pass `70b2af0bbbaf4c73828e7c10a71e044a`)
- Gitea: http://localhost:3001  (user: `gitea` and pass `gitea123`)

```bash
# Create DB for Giteaa
docker exec -it airflow_postgres psql -U airflow -d airflow_metadata -c "CREATE DATABASE gitea;"

# Get password Jenkins
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# Push code to Gitea
git remote set-url origin http://localhost:3001/gitea/mlops_project.git
git push origin test_dvc

# SSH key for jenkins
docker exec jenkins mkdir -p /var/jenkins_home/.ssh
docker exec -it jenkins ssh-keygen -t ed25519 -f /var/jenkins_home/.ssh/id_ed25519 -N ""

# Get SSH key gitea
docker exec jenkins cat /var/jenkins_home/.ssh/id_ed25519.pub
```


# Code Execution Platform

A secure online code execution platform (mini Replit) that runs code in isolated Docker containers. Built with FastAPI and demonstrates modern DevOps practices.

## 🚀 Features

- **Multi-language Support**: Python, C++, Java, JavaScript, Go
- **Secure Execution**: Code runs in isolated Docker containers with resource limits
- **RESTful API**: Well-documented API with Swagger/OpenAPI support
- **Health Monitoring**: Built-in health checks and metrics
- **Container Orchestration**: Docker Compose for easy deployment
- **CI/CD Ready**: GitHub Actions workflow included
- **Production Ready**: Nginx reverse proxy, monitoring with Prometheus/Grafana

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│    Nginx    │────▶│  FastAPI    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Docker    │
                                        │  Containers │
                                        └─────────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)
- 2GB RAM minimum
- Linux/macOS/Windows with WSL2

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/code-executor.git
cd code-executor

# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/health
```

### Manual Docker Build

```bash
# Build the image
docker build -t code-executor .

# Run the container
docker run -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/code:/code \
  code-executor
```

## 📚 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "py",
    "code": "print(\"Hello, World!\")"
  }'
```

### Supported Languages

| Language | ID | Docker Image |
|----------|-----|--------------|
| Python | `py` | python:3.9-slim |
| C++ | `cpp` | gcc:latest |
| Java | `java` | openjdk:17-slim |
| JavaScript | `js` | node:18-slim |
| Go | `go` | golang:1.21-alpine |

## 🔒 Security Features

- **Container Isolation**: Each code execution runs in a separate container
- **Network Disabled**: Containers have no network access
- **Resource Limits**: CPU (0.5 cores) and Memory (128MB) limits
- **Read-only Filesystem**: Prevents malicious file system modifications
- **Execution Timeout**: 10-second timeout for all executions

## 📊 Monitoring

### Prometheus Metrics
- Access at: http://localhost:9090
- Total executions
- Success/failure rates
- Language usage statistics

### Grafana Dashboards
- Access at: http://localhost:3000
- Default credentials: admin/admin

## 🔄 CI/CD

GitHub Actions workflow included for:
- Automated testing
- Docker image building
- Security scanning
- Deployment to AWS

## 🏗️ Development

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload
```

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📦 Deployment

### AWS EC2 Deployment

1. Launch EC2 instance (t2.micro for free tier)
2. Install Docker and Docker Compose
3. Clone repository
4. Run `docker-compose up -d`

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n code-executor
```

## 🗺️ Roadmap

- [ ] Frontend UI (React)
- [ ] User authentication
- [ ] Code persistence
- [ ] Multi-file support
- [ ] Real-time output streaming
- [ ] Kubernetes Helm charts
- [ ] Terraform modules

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Docker for containerization
- The open-source community

---

**Note**: This is a demonstration project for DevOps practices. For production use, additional security measures and scalability considerations should be implemented. 
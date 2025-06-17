# CodeCrate

A secure online code execution platform that allows users to write, compile, and run code in multiple programming languages in a safe, isolated environment.

## Features

- **Multi-language Support**
  - Python 3.9
  - JavaScript (Node.js 18)
  - Java 17
  - C++ (GCC Latest)
  - Go 1.20

- **Secure Execution**
  - Docker container isolation
  - Resource limits (CPU, Memory)
  - Network access disabled
  - Timeout protection

- **Modern UI**
  - Syntax highlighting
  - Real-time code execution
  - Responsive design
  - Dark mode support

## Tech Stack

### Backend
- FastAPI (Python)
- Docker for code isolation
- Uvicorn ASGI server

### Frontend
- React
- Monaco Editor (VS Code's editor)
- Tailwind CSS
- Material-UI

## Prerequisites

- Python 3.9+
- Docker
- Node.js 18+
- npm or yarn

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Salman78687/CodeCrate.git
cd CodeCrate
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Start the backend server:
```bash
uvicorn main:app --reload
```

5. Start the frontend development server:
```bash
cd frontend
npm start
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Select your preferred programming language
3. Write your code in the editor
4. Click "Run Code" to execute
5. View the output in the results panel

## Security Features

- Code execution in isolated Docker containers
- Resource limits to prevent abuse
- Network access disabled for security
- Timeout protection against infinite loops
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Monaco Editor for the code editor component
- Docker for containerization
- FastAPI for the backend framework
- React and Material-UI for the frontend framework

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



## 🗺️ Roadmap

- [ ] Frontend UI (React)
- [ ] User authentication
- [ ] Code persistence
- [ ] Multi-file support
- [ ] Real-time output streaming


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

# CodeCrate: A Secure Online Code Execution Platform

## Project Overview
CodeCrate is a modern, secure online code execution platform that allows users to write, compile, and run code in multiple programming languages in a safe, isolated environment. It's designed to be a lightweight alternative to platforms like Replit, focusing on security and ease of use.

## Core Features

### 1. Multi-language Support
- **Python 3.9**: Using `python:3.9-slim` Docker image
- **JavaScript**: Using `node:18-slim` Docker image
- **Java**: Using `openjdk:17-slim` Docker image
- **C++**: Using `gcc:latest` Docker image
- **Go**: Using `golang:1.20` Docker image

### 2. Security Features
- **Container Isolation**: Each code execution runs in an isolated Docker container
- **Resource Limits**:
  - Memory: 512MB per container
  - CPU: 50% quota per container
  - Network: Disabled for security
  - Timeout: 30 seconds per execution
- **Input Validation**: All code inputs are validated before execution
- **Error Handling**: Comprehensive error handling and sanitization

### 3. Modern UI/UX
- **Code Editor**: Monaco Editor (VS Code's editor) with:
  - Syntax highlighting
  - Auto-completion
  - Line numbers
  - Dark mode
- **Responsive Design**: Works on all device sizes
- **Real-time Feedback**: Immediate execution results
- **Error Handling**: Clear error messages and status indicators

## Technical Architecture

### 1. Frontend (React)
- **Framework**: React with Material-UI
- **Key Components**:
  - Monaco Editor for code editing
  - Material-UI for UI components
  - Axios for API communication
  - React-Toastify for notifications
- **Features**:
  - Real-time code editing
  - Language switching
  - Output display
  - Error handling
  - API health monitoring

### 2. Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **Key Components**:
  - Docker integration for code execution
  - Health check endpoints
  - API versioning
  - Error handling middleware
- **Features**:
  - Asynchronous request handling
  - Container management
  - Resource monitoring
  - Security validation

### 3. Infrastructure
- **Containerization**: Docker for both application and code execution
- **Deployment**: AWS EC2 instance
- **CI/CD**: GitHub Actions for automated deployment
- **Monitoring**: Built-in health checks and logging

## Project Flow

1. **User Interaction**:
   - User writes code in the Monaco Editor
   - Selects programming language
   - Clicks "Run Code" button

2. **Request Processing**:
   - Frontend sends code to backend API
   - Backend validates input
   - Creates isolated Docker container
   - Executes code with resource limits

3. **Code Execution**:
   - Code is written to temporary file
   - Container is created with appropriate language image
   - Code is executed with timeout
   - Output is captured

4. **Response Handling**:
   - Results are sent back to frontend
   - Output is displayed to user
   - Container is cleaned up

## Benefits

1. **Security**:
   - Isolated execution environment
   - Resource limits prevent abuse
   - No network access in containers
   - Input validation and sanitization

2. **User Experience**:
   - Modern, intuitive interface
   - Real-time feedback
   - Multiple language support
   - Syntax highlighting and auto-completion

3. **Developer Experience**:
   - Easy to deploy and maintain
   - Well-documented API
   - Modular architecture
   - Extensible design

4. **Performance**:
   - Fast code execution
   - Efficient resource usage
   - Quick response times
   - Scalable architecture

## Technologies Used

### Frontend
- React
- Material-UI
- Monaco Editor
- Axios
- React-Toastify
- Tailwind CSS

### Backend
- FastAPI
- Uvicorn
- Docker SDK
- Python 3.9+

### Infrastructure
- Docker
- AWS EC2
- GitHub Actions
- Nginx (for production)

## Future Improvements

1. **Features**:
   - File upload support
   - Project management
   - User authentication
   - Code sharing

2. **Security**:
   - Rate limiting
   - User quotas
   - Advanced container security
   - Code analysis

3. **Performance**:
   - Caching
   - Load balancing
   - Container pooling
   - Resource optimization

4. **User Experience**:
   - More language support
   - Custom themes
   - Collaboration features
   - Code templates

## Getting Started

### Prerequisites
- Python 3.9+
- Docker
- Node.js 18+
- npm or yarn

### Installation

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

### Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Select your preferred programming language
3. Write your code in the editor
4. Click "Run Code" to execute
5. View the output in the results panel

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
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from executor import run_code, check_docker_availability, SUPPORTED_LANGUAGES
import time
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with metadata
app = FastAPI(
    title="Code Execution API",
    description="A secure online code execution platform that runs code in isolated Docker containers",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class CodeRequest(BaseModel):
    language: str = Field(..., description="Programming language (py, cpp, java, js, go)")
    code: str = Field(..., description="Source code to execute")
    
    class Config:
        schema_extra = {
            "example": {
                "language": "py",
                "code": "print('Hello, World!')"
            }
        }

class CodeResponse(BaseModel):
    output: Optional[str] = Field(None, description="Program output")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    exitCode: int = Field(..., description="Process exit code")
    executionTime: float = Field(..., description="Execution time in seconds")
    stderr: Optional[str] = Field(None, description="Standard error output")

class HealthResponse(BaseModel):
    status: str
    docker_available: bool
    supported_languages: list
    version: str

# Metrics storage (in production, use Prometheus)
metrics = {
    "total_executions": 0,
    "successful_executions": 0,
    "failed_executions": 0,
    "language_usage": {}
}

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Code Execution API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    docker_available = check_docker_availability()
    
    return HealthResponse(
        status="healthy" if docker_available else "unhealthy",
        docker_available=docker_available,
        supported_languages=list(SUPPORTED_LANGUAGES.keys()),
        version="1.0.0"
    )

@app.get("/api/v1/languages", tags=["Languages"])
async def get_supported_languages():
    """Get list of supported programming languages."""
    return {
        "languages": [
            {
                "id": lang,
                "name": lang.upper(),
                "image": info["image"]
            }
            for lang, info in SUPPORTED_LANGUAGES.items()
        ]
    }

@app.post("/api/v1/execute", response_model=CodeResponse, tags=["Execution"])
async def execute_code(request: CodeRequest):
    """
    Execute code in an isolated Docker container.
    
    - **language**: Programming language (py, cpp, java, js, go)
    - **code**: Source code to execute
    """
    logger.info(f"Received execution request for language: {request.language}")
    
    # Record metrics
    metrics["total_executions"] += 1
    metrics["language_usage"][request.language] = metrics["language_usage"].get(request.language, 0) + 1
    
    # Validate language
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language: {request.language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}"
        )
    
    # Check Docker availability
    if not check_docker_availability():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Docker service is not available"
        )
    
    # Execute code
    start_time = time.time()
    try:
        result = run_code(request.language, request.code)
        execution_time = time.time() - start_time
        
        # Update metrics
        if "error" not in result:
            metrics["successful_executions"] += 1
        else:
            metrics["failed_executions"] += 1
        
        # Create response, ensuring exitCode is not duplicated
        response_data = {
            "output": result.get("output"),
            "error": result.get("error"),
            "exitCode": result.get("exitCode", 0),
            "executionTime": execution_time,
            "stderr": result.get("stderr")
        }
        
        response = CodeResponse(**response_data)
        
        logger.info(f"Execution completed in {execution_time:.2f}s with exit code: {response.exitCode}")
        return response
        
    except Exception as e:
        execution_time = time.time() - start_time
        metrics["failed_executions"] += 1
        logger.error(f"Execution failed: {str(e)}", exc_info=True)
        
        return CodeResponse(
            error=f"Internal server error: {str(e)}",
            exitCode=-1,
            executionTime=execution_time
        )

@app.get("/api/v1/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get execution metrics for monitoring."""
    return metrics

# Backward compatibility endpoint
@app.post("/execute", response_model=CodeResponse, tags=["Execution"], deprecated=True)
async def execute_code_legacy(request: CodeRequest):
    """Legacy endpoint - use /api/v1/execute instead."""
    return await execute_code(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
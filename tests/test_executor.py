import pytest
from executor import run_code, check_docker_availability

def test_docker_availability():
    """Test if Docker daemon is accessible."""
    assert check_docker_availability() is True

def test_python_execution():
    """Test Python code execution."""
    code = "print('Hello, World!')"
    result = run_code("py", code)
    assert result["exitCode"] == 0
    assert "Hello, World!" in result["output"]

def test_cpp_execution():
    """Test C++ code execution."""
    code = """
    #include <iostream>
    int main() {
        std::cout << "Hello from C++!" << std::endl;
        return 0;
    }
    """
    result = run_code("cpp", code)
    assert result["exitCode"] == 0
    assert "Hello from C++!" in result["output"]

def test_java_execution():
    """Test Java code execution."""
    code = """
    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello from Java!");
        }
    }
    """
    result = run_code("java", code)
    assert result["exitCode"] == 0
    assert "Hello from Java!" in result["output"]

def test_js_execution():
    """Test JavaScript code execution."""
    code = "console.log('Hello from JavaScript!')"
    result = run_code("js", code)
    assert result["exitCode"] == 0
    assert "Hello from JavaScript!" in result["output"]

def test_go_execution():
    """Test Go code execution."""
    code = """
    package main
    import "fmt"
    func main() {
        fmt.Println("Hello from Go!")
    }
    """
    result = run_code("go", code)
    assert result["exitCode"] == 0
    assert "Hello from Go!" in result["output"]

def test_invalid_language():
    """Test execution with invalid language."""
    result = run_code("invalid", "print('test')")
    assert result["exitCode"] == -1
    assert "Unsupported language" in result["error"]

def test_timeout():
    """Test code execution timeout."""
    code = "import time; time.sleep(40)"  # Should timeout after 30 seconds
    result = run_code("py", code)
    assert result["exitCode"] == -1
    assert "timed out" in result["error"] 
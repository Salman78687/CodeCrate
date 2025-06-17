import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Box, Paper, Typography, Button, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import Editor from '@monaco-editor/react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import axios from 'axios';
import { styled } from '@mui/material/styles';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2563eb',
      dark: '#1d4ed8',
    },
    background: {
      default: '#0f172a',
      paper: '#1e293b',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.1rem',
      color: '#94a3b8',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '0.5rem',
          padding: '0.75rem 1.5rem',
          fontSize: '1rem',
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: '1rem',
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        },
      },
    },
  },
});

const StyledContainer = styled(Container)(({ theme }) => ({
  padding: '2rem',
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  gap: '1.5rem',
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: '2rem',
  animation: 'fadeIn 0.5s ease-out',
}));

const StyledFormControl = styled(FormControl)(({ theme }) => ({
  marginBottom: '1.5rem',
  animation: 'fadeIn 0.5s ease-out',
  '& .MuiInputLabel-root': {
    color: theme.palette.text.secondary,
  },
  '& .MuiSelect-select': {
    backgroundColor: theme.palette.background.default,
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: '0.5rem',
    padding: '0.75rem',
    '&:hover': {
      borderColor: theme.palette.primary.main,
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    },
  },
}));

const OutputBox = styled(Box)(({ theme, error, success }) => ({
  marginTop: '1.5rem',
  padding: '1rem',
  backgroundColor: theme.palette.background.default,
  border: `1px solid ${error ? '#ef4444' : success ? '#22c55e' : theme.palette.divider}`,
  borderRadius: '0.5rem',
  whiteSpace: 'pre-wrap',
  fontFamily: '"JetBrains Mono", monospace',
  fontSize: '0.9rem',
  lineHeight: 1.6,
  animation: error ? 'errorShake 0.5s ease-out' : success ? 'successPulse 0.5s ease-out' : 'fadeIn 0.3s ease-out',
  color: error ? '#ef4444' : success ? '#22c55e' : theme.palette.text.primary,
}));

const defaultCodeSnippets = {
  python: '# Write your Python code here\nprint("Hello, World!")',
  cpp: '// Write your C++ code here\n#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
  java: '// Write your Java code here\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
  javascript: '// Write your JavaScript code here\nconsole.log("Hello, World!");',
  go: '// Write your Go code here\npackage main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}'
};

const languageToMonacoLanguage = {
  python: 'python',
  cpp: 'cpp',
  java: 'java',
  javascript: 'javascript',
  go: 'go'
};

const languages = [
  { id: 'python', name: 'Python' },
  { id: 'cpp', name: 'C++' },
  { id: 'java', name: 'Java' },
  { id: 'javascript', name: 'JavaScript' },
  { id: 'go', name: 'Go' }
];

// API configuration
const API_URL = 'http://44.203.253.148:8001';

function App() {
  const [code, setCode] = useState(defaultCodeSnippets.python);
  const [language, setLanguage] = useState('python');
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');

  // Check API availability on component mount
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await axios.get(`${API_URL}/health`);
        setApiStatus(response.data.status === 'healthy' ? 'available' : 'unhealthy');
      } catch (error) {
        setApiStatus('unavailable');
        console.error('API health check failed:', error);
      }
    };
    checkApiStatus();
  }, []);

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    setCode(defaultCodeSnippets[newLanguage]);
  };

  const handleExecute = async () => {
    if (apiStatus !== 'available') {
      setOutput('API is not available. Please check your connection.');
      setIsError(true);
      return;
    }

    setIsLoading(true);
    setIsError(false);
    setIsSuccess(false);
    setOutput('');

    try {
      const response = await axios.post(`${API_URL}/api/v1/execute`, {
        language,
        code
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        timeout: 120000  // 2 minutes timeout
      });
      
      if (response.data.error) {
        setIsError(true);
        setOutput(typeof response.data.error === 'string' ? response.data.error : JSON.stringify(response.data.error));
      } else {
        setIsSuccess(true);
        setOutput(response.data.output || '');
      }
    } catch (error) {
      setIsError(true);
      const errorMessage = error.response?.data?.detail || 
                          (typeof error.response?.data === 'object' ? JSON.stringify(error.response.data) : error.message) || 
                          'An error occurred';
      setOutput(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
          CodeCrate
        </h1>
        <p className="text-center text-gray-300 mb-12 text-lg">
          A secure online code execution platform
        </p>
        <StyledContainer maxWidth="lg">
          <StyledPaper>
            <Typography variant="h1" component="h1" gutterBottom>
              ⚡ CodeCrate
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              A secure online code execution platform
            </Typography>
            
            <StyledFormControl fullWidth>
              <InputLabel>Language</InputLabel>
              <Select
                value={language}
                label="Language"
                onChange={(e) => handleLanguageChange(e.target.value)}
              >
                {languages.map((lang) => (
                  <MenuItem key={lang.id} value={lang.id}>
                    {lang.name}
                  </MenuItem>
                ))}
              </Select>
            </StyledFormControl>

            <Box sx={{ height: '400px', mb: 2 }}>
              <Editor
                height="100%"
                language={languageToMonacoLanguage[language]}
                value={code}
                onChange={(value) => setCode(value)}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  fontFamily: '"JetBrains Mono", monospace',
                  lineHeight: 1.6,
                  automaticLayout: true,
                }}
              />
            </Box>

            <Button
              variant="contained"
              color="primary"
              onClick={handleExecute}
              disabled={isLoading}
              sx={{ mr: 2 }}
            >
              {isLoading ? 'Executing...' : 'Run Code'}
            </Button>

            <Box
              sx={{
                mt: 2,
                p: 2,
                bgcolor: 'background.paper',
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'divider',
                display: 'flex',
                flexDirection: 'column',
                gap: 2
              }}
              success={isSuccess ? "true" : undefined}
              error={isError ? "true" : undefined}
            >
              {output || 'No output yet'}
            </Box>

            <Box sx={{ mt: 4 }}>
              <Typography variant="h3" gutterBottom>
                Statistics
              </Typography>
              <Box sx={{ 
                p: 2, 
                bgcolor: 'background.default', 
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'divider'
              }}>
                <Typography variant="body1" sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <span>Total Executions:</span>
                  <span>0</span>
                </Typography>
                <Typography variant="body1" sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <span>Success Rate:</span>
                  <span>0%</span>
                </Typography>
                <Typography variant="body1" sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Average Execution Time:</span>
                  <span>0ms</span>
                </Typography>
              </Box>
            </Box>
          </StyledPaper>
        </StyledContainer>
      </div>
      <ToastContainer 
        position="bottom-right"
        theme="dark"
        toastStyle={{
          backgroundColor: '#1e293b',
          color: '#f8fafc',
        }}
      />
    </ThemeProvider>
  );
}

export default App; 
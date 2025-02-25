import React, { useState, useEffect } from 'react';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline, 
  Box, 
  CircularProgress,
  Typography
} from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import BattlecardDashboard from './BattlecardDashboard';
import BattlecardGenerator from './BattlecardGenerator';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#6c5ce7',
      light: '#a29bfe',
      dark: '#5441e0',
    },
    success: {
      main: '#00b894',
      light: '#55efc4',
      dark: '#00a382',
    },
    warning: {
      main: '#fdcb6e',
      light: '#ffeaa7',
      dark: '#f0b14c',
    },
    error: {
      main: '#d63031',
      light: '#ff7675',
      dark: '#b71c1c',
    },
    background: {
      default: '#f5f7fb', 
      paper: '#ffffff'
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 700,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0 6px 12px rgba(0,0,0,0.1)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
          border: '1px solid rgba(0,0,0,0.03)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 12,
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          '&.Mui-selected': {
            backgroundColor: 'rgba(25, 118, 210, 0.08)',
            '&:hover': {
              backgroundColor: 'rgba(25, 118, 210, 0.12)',
            },
          },
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          minWidth: 40,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 600,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
      },
    },
  },
});

// Create Query Client 
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 60000,
    },
  },
});

// Auth Context
const AuthContext = React.createContext({
  isAuthenticated: false,
  user: null,
  login: () => {},
  logout: () => {},
});

const useAuth = () => React.useContext(AuthContext);

// Auth Provider
const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulate authentication check on app load
  useEffect(() => {
    const checkAuth = async () => {
      // In a real app, this would check for a valid token in localStorage
      // and validate it with the backend
      try {
        const token = localStorage.getItem('token');
        if (token) {
          // Simulate API call to validate token and get user data
          await new Promise(resolve => setTimeout(resolve, 500));
          setUser({
            id: '1',
            name: 'Jamie Smith',
            email: 'jamie@example.com',
            role: 'admin',
            avatar: '/api/placeholder/64/64'
          });
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    // Simulate login API call
    setLoading(true);
    try {
      // In a real app, this would make an API call to your backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For demo purposes, accept any email/password
      const user = {
        id: '1',
        name: 'Jamie Smith',
        email: email,
        role: 'admin',
        avatar: '/api/placeholder/64/64'
      };
      
      // Store token in localStorage
      localStorage.setItem('token', 'demo-token-12345');
      
      setUser(user);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.message || 'Login failed. Please check your credentials.' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    if (!email || !password) {
      setError('Please enter both email and password');
      setIsLoading(false);
      return;
    }

    try {
      const result = await login(email, password);
      if (!result.success) {
        setError(result.error);
      }
    } catch (error) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box 
      sx={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2
      }}
    >
      <Box 
        sx={{ 
          maxWidth: 400, 
          width: '100%', 
          bgcolor: 'background.paper',
          borderRadius: 3,
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          p: 4
        }}
      >
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Battlecard Platform
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sign in to access your battlecards and competitor insights
          </Typography>
        </Box>

        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Email
            </Typography>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #E0E0E0',
                fontSize: '16px'
              }}
              placeholder="Enter your email"
            />
          </Box>

          <Box sx={{ mb: 4 }}>
            <Typography variant="subtitle2" gutterBottom>
              Password
            </Typography>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #E0E0E0',
                fontSize: '16px'
              }}
              placeholder="Enter your password"
            />
          </Box>

          {error && (
            <Box 
              sx={{ 
                p: 2, 
                mb: 3, 
                bgcolor: 'error.light',
                color: 'error.dark',
                borderRadius: 1,
                fontSize: '0.875rem'
              }}
            >
              {error}
            </Box>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 500,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: isLoading ? 0.7 : 1
            }}
          >
            {isLoading ? (
              <>
                <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </button>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Demo credentials: any email and password
            </Typography>
          </Box>
        </form>
      </Box>
    </Box>
  );
};

// App Entry Component
const BattlecardApp = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
        {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
      </QueryClientProvider>
    </ThemeProvider>
  );
};

// App Content with Auth Check
const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          bgcolor: 'background.default'
        }}
      >
        <CircularProgress size={40} />
        <Typography sx={{ mt: 2 }} variant="h6">
          Loading Battlecard Platform...
        </Typography>
      </Box>
    );
  }

  return isAuthenticated ? <BattlecardDashboard /> : <Login />;
};

export default BattlecardApp;
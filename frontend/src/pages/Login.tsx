import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Divider,
  Grid,
  TextField,
  Typography,
  Alert,
  Paper,
} from '@mui/material';
import {
  Google as GoogleIcon,
  Microsoft as MicrosoftIcon,
  AutoAwesome as AIIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const benefits = [
  {
    icon: <AIIcon fontSize="large" color="primary" />,
    title: 'AI-Powered Battlecards',
    description: 'Generate customized sales battlecards with advanced AI technology',
  },
  {
    icon: <SpeedIcon fontSize="large" color="primary" />,
    title: 'Real-Time Updates',
    description: 'Stay ahead with instant competitor and market intelligence',
  },
  {
    icon: <SecurityIcon fontSize="large" color="primary" />,
    title: 'Enterprise Security',
    description: 'SOC2 compliant with role-based access control',
  },
];

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  const handleSSOLogin = (provider: string) => {
    // Implement SSO login logic
    console.log(`Login with ${provider}`);
  };

  return (
    <Container maxWidth="lg" sx={{ height: '100vh', py: 4 }}>
      <Grid container spacing={4} alignItems="center" sx={{ height: '100%' }}>
        <Grid item xs={12} md={7}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h3" gutterBottom color="primary" fontWeight="bold">
              Welcome to Battlecard Platform
            </Typography>
            <Typography variant="h5" color="text.secondary" gutterBottom>
              Your AI-powered competitive intelligence solution
            </Typography>
          </Box>

          <Grid container spacing={4}>
            {benefits.map((benefit, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    height: '100%',
                    backgroundColor: 'background.default',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                  }}
                >
                  <Box sx={{ mb: 2 }}>{benefit.icon}</Box>
                  <Typography variant="h6" gutterBottom>
                    {benefit.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {benefit.description}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card elevation={4}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" gutterBottom align="center">
                Sign In
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Email"
                  variant="outlined"
                  margin="normal"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  variant="outlined"
                  margin="normal"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  type="submit"
                  sx={{ mt: 3 }}
                >
                  Sign In
                </Button>
              </form>

              <Box sx={{ my: 3 }}>
                <Divider>
                  <Typography variant="body2" color="text.secondary">
                    OR
                  </Typography>
                </Divider>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="outlined"
                    size="large"
                    startIcon={<GoogleIcon />}
                    onClick={() => handleSSOLogin('google')}
                  >
                    Sign in with Google
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="outlined"
                    size="large"
                    startIcon={<MicrosoftIcon />}
                    onClick={() => handleSSOLogin('microsoft')}
                  >
                    Sign in with Microsoft
                  </Button>
                </Grid>
              </Grid>

              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Don't have an account?{' '}
                  <Button color="primary" onClick={() => navigate('/signup')}>
                    Request Access
                  </Button>
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Login; 
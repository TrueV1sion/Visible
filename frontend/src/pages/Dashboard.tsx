import React from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Grid,
  Typography,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  RateReview as ReviewIcon,
  AutoAwesome as AIIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import RecentBattlecards from '../components/dashboard/RecentBattlecards';
import CompetitorUpdates from '../components/dashboard/CompetitorUpdates';
import ObjectionLibrary from '../components/dashboard/ObjectionLibrary';
import NotificationCenter from '../components/notifications/NotificationCenter';

const roleBasedActions = {
  admin: [
    { label: 'Manage Users', path: '/admin/users', icon: null },
    { label: 'Data Sources', path: '/admin/integrations', icon: null },
    { label: 'Audit Logs', path: '/admin/audit', icon: null },
  ],
  sales: [
    { label: 'Frequent Objections', path: '/objections', icon: null },
    { label: 'Competitor Comparisons', path: '/comparisons', icon: null },
    { label: 'Pricing Updates', path: '/pricing', icon: null },
  ],
  marketing: [
    { label: 'Use Cases', path: '/use-cases', icon: null },
    { label: 'Case Studies', path: '/case-studies', icon: null },
    { label: 'Messaging Framework', path: '/messaging', icon: null },
  ],
};

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const userRole = user?.role || 'sales';

  const handleCreateBattlecard = () => {
    navigate('/battlecards/create');
  };

  const handleReviewPending = () => {
    navigate('/battlecards/pending');
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Welcome back, {user?.name}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's what's happening in your competitive landscape
          </Typography>
        </Box>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateBattlecard}
            sx={{ mr: 2 }}
          >
            Create Battlecard
          </Button>
          {(userRole === 'admin' || userRole === 'marketing') && (
            <Button
              variant="outlined"
              startIcon={<ReviewIcon />}
              onClick={handleReviewPending}
            >
              Review Pending
            </Button>
          )}
        </Box>
      </Box>

      <Grid container spacing={4}>
        {/* Main Content Area */}
        <Grid item xs={12} lg={8}>
          <Grid container spacing={3}>
            {/* Recent Battlecard Activity */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Battlecard Activity
                  </Typography>
                  <RecentBattlecards limit={5} />
                </CardContent>
              </Card>
            </Grid>

            {/* Competitor Updates */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      Competitor Updates
                    </Typography>
                  </Box>
                  <CompetitorUpdates />
                </CardContent>
              </Card>
            </Grid>

            {/* Objection Handling */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AIIcon color="secondary" sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      AI-Suggested Objection Handling
                    </Typography>
                  </Box>
                  <ObjectionLibrary />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Right Sidebar */}
        <Grid item xs={12} lg={4}>
          {/* Quick Actions */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                {roleBasedActions[userRole as keyof typeof roleBasedActions]?.map((action, index) => (
                  <Grid item xs={12} key={index}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={action.icon}
                      onClick={() => navigate(action.path)}
                    >
                      {action.label}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notifications
              </Typography>
              <NotificationCenter />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 
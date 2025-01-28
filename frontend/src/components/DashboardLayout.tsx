import React from 'react';
import { Box, Container, Grid, Paper, Typography } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import RecentUpdates from './dashboard/RecentUpdates';
import CompetitorUpdates from './dashboard/CompetitorUpdates';
import LeadGeneration from './dashboard/LeadGeneration';
import FeatureUpdates from './dashboard/FeatureUpdates';
import ObjectionLibrary from './dashboard/ObjectionLibrary';

interface DashboardProps {
  children?: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardProps> = ({ children }) => {
  const { user } = useAuth();

  const renderRoleBasedContent = () => {
    switch (user?.role) {
      case 'SALES':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <CompetitorUpdates />
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <ObjectionLibrary />
              </Paper>
            </Grid>
          </Grid>
        );
      case 'MARKETING':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <LeadGeneration />
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <RecentUpdates type="marketing" />
              </Paper>
            </Grid>
          </Grid>
        );
      case 'PRODUCT':
      case 'BUSINESS_DEVELOPMENT':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <FeatureUpdates />
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <RecentUpdates type="product" />
              </Paper>
            </Grid>
          </Grid>
        );
      default:
        return (
          <Typography variant="h6" color="text.secondary">
            Please contact your administrator to set up your role.
          </Typography>
        );
    }
  };

  return (
    <Box sx={{ flexGrow: 1, height: '100vh', overflow: 'auto' }}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {renderRoleBasedContent()}
        {children}
      </Container>
    </Box>
  );
};

export default DashboardLayout; 
import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Divider,
  Typography,
  useTheme
} from '@mui/material';
import {
  Dashboard,
  Description,
  Insights,
  Settings,
  TrendingUp,
  PeopleAlt as PeopleAltIcon // Added for Customers
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 240;

const menuItems = [
  { path: '/dashboard', label: 'Dashboard', icon: Dashboard },
  { path: '/battlecards', label: 'Battlecards', icon: Description },
  { path: '/customers', label: 'Payer Customers', icon: PeopleAltIcon }, // Added new item
  { path: '/competitor-insights', label: 'Competitor Insights', icon: TrendingUp },
  { path: '/market-analysis', label: 'Market Analysis', icon: Insights },
  { path: '/settings', label: 'Settings', icon: Settings },
];

const MainNavigation: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: theme.palette.background.default,
          borderRight: `1px solid ${theme.palette.divider}`,
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" noWrap component="div">
          Battlecard Platform
        </Typography>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isSelected = location.pathname === item.path;

          return (
            <ListItem
              button
              key={item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                mb: 0.5,
                borderRadius: 1,
                mx: 1,
                backgroundColor: isSelected
                  ? theme.palette.action.selected
                  : 'transparent',
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                },
              }}
            >
              <ListItemIcon>
                <Icon
                  color={isSelected ? 'primary' : 'inherit'}
                  sx={{ fontSize: 24 }}
                />
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  color: isSelected ? 'primary' : 'inherit',
                  fontWeight: isSelected ? 600 : 400,
                }}
              />
            </ListItem>
          );
        })}
      </List>
      <Box sx={{ mt: 'auto', p: 2 }}>
        <Typography variant="body2" color="text.secondary">
          {user?.name}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {user?.role}
        </Typography>
      </Box>
    </Drawer>
  );
};

export default MainNavigation; 
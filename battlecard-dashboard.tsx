import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Container, 
  Drawer,
  Grid, 
  IconButton, 
  LinearProgress,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper, 
  Typography, 
  useTheme,
  useMediaQuery,
  Chip,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  TextField,
  InputAdornment
} from '@mui/material';

import {
  BarChart,
  Home,
  AlignJustify,
  FileText,
  Users,
  TrendingUp,
  MessageSquare,
  Settings,
  Bell,
  Search,
  FileBarChart,
  LogOut,
  ChevronDown,
  Star,
  User,
  Calendar,
  RefreshCw,
  Zap,
  Filter,
  PlusCircle,
  Bookmark
} from 'lucide-react';

import BattlecardGenerator from './BattlecardGenerator';

// Sample data
const RECENT_BATTLECARDS = [
  { id: 'bc1', title: 'Competitor A Enterprise', competitor: 'Competitor A', lastModified: '2024-02-15', views: 245 },
  { id: 'bc2', title: 'Competitor B Cloud Suite', competitor: 'Competitor B', lastModified: '2024-02-10', views: 189 },
  { id: 'bc3', title: 'Competitor C Analytics Platform', competitor: 'Competitor C', lastModified: '2024-02-05', views: 167 },
  { id: 'bc4', title: 'Competitor D Security Solution', competitor: 'Competitor D', lastModified: '2024-01-28', views: 134 }
];

const COMPETITOR_UPDATES = [
  { 
    id: 'update1', 
    competitor: 'Competitor A', 
    title: 'New Enterprise Plan Released', 
    description: 'Competitor A has launched a new Enterprise tier with advanced security features and dedicated support.',
    date: '2024-02-18',
    type: 'pricing',
    impact: 'medium' 
  },
  { 
    id: 'update2', 
    competitor: 'Competitor B', 
    title: 'European Market Expansion', 
    description: 'Competitor B announced opening new offices in Berlin and Paris as part of their European expansion strategy.',
    date: '2024-02-14',
    type: 'market',
    impact: 'high' 
  },
  { 
    id: 'update3', 
    competitor: 'Competitor C', 
    title: 'AI Integration Partnership', 
    description: 'Competitor C has partnered with an AI startup to enhance their analytics capabilities.',
    date: '2024-02-12',
    type: 'feature',
    impact: 'high' 
  }
];

const NOTIFICATIONS = [
  { id: 'n1', title: 'Competitor A Battlecard Updated', time: '2 hours ago' },
  { id: 'n2', title: 'New Market Intelligence Available', time: '5 hours ago' },
  { id: 'n3', title: 'Competitor B Released New Feature', time: '1 day ago' },
  { id: 'n4', title: '3 Battlecards Need Review', time: '2 days ago' }
];

// Main Dashboard Component
const BattlecardDashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // State for drawer
  const [drawerOpen, setDrawerOpen] = useState(!isMobile);
  
  // State for current section
  const [currentSection, setCurrentSection] = useState('dashboard');
  
  // State for profile menu
  const [profileMenuAnchor, setProfileMenuAnchor] = useState(null);
  
  // State for notifications menu
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);
  
  // Update drawer state on screen size change
  useEffect(() => {
    setDrawerOpen(!isMobile);
  }, [isMobile]);
  
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  const handleSectionChange = (section) => {
    setCurrentSection(section);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };
  
  const handleProfileMenuOpen = (event) => {
    setProfileMenuAnchor(event.currentTarget);
  };
  
  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };
  
  const handleNotificationsOpen = (event) => {
    setNotificationsAnchor(event.currentTarget);
  };
  
  const handleNotificationsClose = () => {
    setNotificationsAnchor(null);
  };
  
  // Render sidebar navigation
  const renderSidebar = () => {
    const navItems = [
      { id: 'dashboard', label: 'Dashboard', icon: <Home size={20} /> },
      { id: 'battlecards', label: 'Battlecards', icon: <FileText size={20} /> },
      { id: 'competitors', label: 'Competitors', icon: <TrendingUp size={20} /> },
      { id: 'objections', label: 'Objection Library', icon: <MessageSquare size={20} /> },
      { id: 'reports', label: 'Reports', icon: <BarChart size={20} /> },
      { id: 'team', label: 'Team', icon: <Users size={20} /> },
      { id: 'settings', label: 'Settings', icon: <Settings size={20} /> }
    ];
    
    return (
      <Drawer
        variant={isMobile ? "temporary" : "persistent"}
        open={drawerOpen}
        onClose={handleDrawerToggle}
        sx={{
          width: 240,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
            backgroundColor: theme.palette.background.default,
            borderRight: `1px solid ${theme.palette.divider}`
          },
        }}
      >
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
          <Zap size={24} color={theme.palette.primary.main} />
          <Typography variant="h6" sx={{ ml: 1, fontWeight: 600 }}>
            Battlecard Pro
          </Typography>
        </Box>
        
        <Divider />
        
        <List component="nav">
          {navItems.map((item) => (
            <ListItemButton
              key={item.id}
              selected={currentSection === item.id}
              onClick={() => handleSectionChange(item.id)}
              sx={{
                borderRadius: 1,
                mb: 0.5,
                mx: 1
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
              {item.id === 'battlecards' && (
                <Badge badgeContent={4} color="primary" variant="dot" />
              )}
            </ListItemButton>
          ))}
        </List>
        
        <Box sx={{ mt: 'auto', p: 2 }}>
          <Paper 
            elevation={0} 
            sx={{ 
              p: 2, 
              bgcolor: 'primary.main', 
              color: 'primary.contrastText',
              borderRadius: 2
            }}
          >
            <Typography variant="subtitle2" fontWeight={600}>
              PRO Plan Active
            </Typography>
            <Typography variant="body2" sx={{ mb: 1, opacity: 0.8 }}>
              Your plan expires in 30 days
            </Typography>
            <Button 
              size="small" 
              variant="outlined" 
              color="inherit" 
              sx={{ borderColor: 'rgba(255,255,255,0.5)' }}
            >
              Manage Subscription
            </Button>
          </Paper>
        </Box>
      </Drawer>
    );
  };
  
  // Render header with search and notifications
  const renderHeader = () => {
    return (
      <Box
        sx={{
          py: 1.5,
          px: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.background.default
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton
            color="inherit"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <AlignJustify size={24} />
          </IconButton>
          
          <TextField
            placeholder="Search battlecards, competitors..."
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search size={18} />
                </InputAdornment>
              ),
            }}
            sx={{
              width: { xs: 180, sm: 300 },
              '& .MuiOutlinedInput-root': {
                borderRadius: 4
              }
            }}
          />
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton 
            color="inherit" 
            onClick={handleNotificationsOpen}
            sx={{ mr: 1 }}
          >
            <Badge badgeContent={4} color="error">
              <Bell size={20} />
            </Badge>
          </IconButton>
          
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              cursor: 'pointer'
            }}
            onClick={handleProfileMenuOpen}
          >
            <Avatar 
              src="/api/placeholder/32/32" 
              alt="User" 
              sx={{ 
                width: 32, 
                height: 32,
                mr: 1 
              }} 
            />
            <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
              <Typography variant="subtitle2" component="span">
                Jamie Smith
              </Typography>
              <Typography 
                variant="caption" 
                component="span" 
                color="text.secondary"
                sx={{ ml: 1 }}
              >
                Admin
              </Typography>
            </Box>
            <ChevronDown size={16} />
          </Box>
          
          <Menu
            anchorEl={profileMenuAnchor}
            open={Boolean(profileMenuAnchor)}
            onClose={handleProfileMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem onClick={handleProfileMenuClose}>
              <ListItemIcon>
                <User size={18} />
              </ListItemIcon>
              <ListItemText>My Profile</ListItemText>
            </MenuItem>
            <MenuItem onClick={handleProfileMenuClose}>
              <ListItemIcon>
                <Settings size={18} />
              </ListItemIcon>
              <ListItemText>Account Settings</ListItemText>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleProfileMenuClose}>
              <ListItemIcon>
                <LogOut size={18} />
              </ListItemIcon>
              <ListItemText>Logout</ListItemText>
            </MenuItem>
          </Menu>
          
          <Menu
            anchorEl={notificationsAnchor}
            open={Boolean(notificationsAnchor)}
            onClose={handleNotificationsClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            sx={{ width: 320 }}
            PaperProps={{
              sx: { width: 320, maxHeight: 450 }
            }}
          >
            <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="subtitle1" fontWeight={600}>
                Notifications
              </Typography>
              <Button size="small">Mark all as read</Button>
            </Box>
            <Divider />
            <List sx={{ p: 0 }}>
              {NOTIFICATIONS.map(notification => (
                <ListItem 
                  key={notification.id}
                  disablePadding
                  secondaryAction={
                    <Typography variant="caption" color="text.secondary">
                      {notification.time}
                    </Typography>
                  }
                >
                  <ListItemButton>
                    <ListItemText 
                      primary={notification.title}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
            <Divider />
            <Box sx={{ p: 1, display: 'flex', justifyContent: 'center' }}>
              <Button size="small" endIcon={<ChevronDown size={16} />}>
                View All Notifications
              </Button>
            </Box>
          </Menu>
        </Box>
      </Box>
    );
  };
  
  // Render dashboard content
  const renderDashboard = () => {
    return (
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" gutterBottom fontWeight={600}>
              Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Welcome back! Here's what's happening in your competitive landscape.
            </Typography>
          </Box>
          <Button 
            variant="contained" 
            startIcon={<PlusCircle size={18} />}
            onClick={() => handleSectionChange('generator')}
          >
            New Battlecard
          </Button>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" variant="overline">
                  Active Battlecards
                </Typography>
                <Typography variant="h4" fontWeight={600} sx={{ my: 1 }}>
                  42
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip 
                    label="+12% from last month" 
                    size="small" 
                    color="success" 
                    sx={{ height: 20, fontSize: '0.75rem' }} 
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" variant="overline">
                  Tracked Competitors
                </Typography>
                <Typography variant="h4" fontWeight={600} sx={{ my: 1 }}>
                  16
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip 
                    label="+3 new this month" 
                    size="small" 
                    color="success" 
                    sx={{ height: 20, fontSize: '0.75rem' }} 
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" variant="overline">
                  Total Views
                </Typography>
                <Typography variant="h4" fontWeight={600} sx={{ my: 1 }}>
                  3,842
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip 
                    label="+18.5% from last month" 
                    size="small" 
                    color="success" 
                    sx={{ height: 20, fontSize: '0.75rem' }} 
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" variant="overline">
                  AI-Generated Content
                </Typography>
                <Typography variant="h4" fontWeight={600} sx={{ my: 1 }}>
                  67%
                </Typography>
                <Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={67} 
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} lg={8}>
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">
                Recent Competitor Updates
              </Typography>
              <Button 
                endIcon={<Filter size={16} />}
                size="small"
              >
                Filter
              </Button>
            </Box>
            {COMPETITOR_UPDATES.map(update => (
              <Card key={update.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip label={update.competitor} size="small" />
                      <Chip 
                        label={update.type} 
                        size="small" 
                        variant="outlined" 
                      />
                      <Chip 
                        label={update.impact === 'high' ? 'High Impact' : 'Medium Impact'} 
                        size="small" 
                        color={update.impact === 'high' ? 'error' : 'warning'} 
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {update.date}
                    </Typography>
                  </Box>
                  <Typography variant="subtitle1" gutterBottom fontWeight={500}>
                    {update.title}
                  </Typography>
                  <Typography variant="body2">
                    {update.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Button 
                      size="small" 
                      variant="outlined" 
                      startIcon={<RefreshCw size={16} />}
                    >
                      Update Battlecards
                    </Button>
                    <Button 
                      size="small" 
                      variant="outlined" 
                      startIcon={<Bookmark size={16} />}
                    >
                      Save
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            ))}
            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Button endIcon={<ChevronDown size={16} />}>
                Load More Updates
              </Button>
            </Box>
          </Grid>
          
          <Grid item xs={12} lg={4}>
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">
                Recent Battlecards
              </Typography>
              <Button 
                endIcon={<ChevronDown size={16} />}
                size="small"
              >
                View All
              </Button>
            </Box>
            
            {RECENT_BATTLECARDS.map(card => (
              <Card key={card.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight={500}>
                        {card.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 0.5 }}>
                        <Chip label={card.competitor} size="small" />
                        <Typography variant="caption" color="text.secondary">
                          Updated: {card.lastModified}
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Star size={16} color={theme.palette.warning.main} />
                      <Typography variant="caption" color="text.secondary">
                        {card.views} views
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Button size="small" variant="outlined">
                      View
                    </Button>
                    <Button size="small" variant="outlined">
                      Edit
                    </Button>
                    <Button 
                      size="small" 
                      variant="outlined" 
                      startIcon={<FileBarChart size={16} />}
                    >
                      Share
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            ))}
            
            <Card sx={{ bgcolor: 'primary.main', color: 'primary.contrastText', position: 'relative', overflow: 'hidden', mt: 3 }}>
              <Box
                sx={{
                  position: 'absolute',
                  top: -15,
                  right: -15,
                  width: 130,
                  height: 130,
                  borderRadius: '50%',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  bottom: -20,
                  left: -20,
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                }}
              />
              <CardContent>
                <Box sx={{ position: 'relative', zIndex: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    Need a new battlecard?
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2, opacity: 0.8 }}>
                    Generate AI-powered battlecards in minutes with our wizard.
                  </Typography>
                  <Button 
                    variant="contained" 
                    color="secondary"
                    onClick={() => handleSectionChange('generator')}
                  >
                    Create New Battlecard
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    );
  };
  
  // Render main content based on current section
  const renderContent = () => {
    switch (currentSection) {
      case 'dashboard':
        return renderDashboard();
      case 'generator':
        return <BattlecardGenerator />;
      default:
        return (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h5" sx={{ mt: 4 }}>
              {currentSection.charAt(0).toUpperCase() + currentSection.slice(1)} Section
            </Typography>
            <Typography color="text.secondary" sx={{ mt: 1 }}>
              This section is under development.
            </Typography>
            <Button 
              variant="contained" 
              sx={{ mt: 3 }}
              onClick={() => handleSectionChange('dashboard')}
            >
              Back to Dashboard
            </Button>
          </Box>
        );
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {renderSidebar()}
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100vh',
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: theme.palette.grey[50]
        }}
      >
        {renderHeader()}
        {renderContent()}
      </Box>
    </Box>
  );
};

export default BattlecardDashboard;
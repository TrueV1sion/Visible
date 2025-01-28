import React, { useState } from 'react';
import {
  Badge,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Divider,
  Chip,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  TrendingUp,
  Description,
  Campaign,
  Build,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { fetchNotifications, markAsRead } from '../../api/notifications';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'competitor' | 'battlecard' | 'marketing' | 'feature';
  timestamp: string;
  read: boolean;
}

const NotificationCenter: React.FC = () => {
  const [open, setOpen] = useState(false);

  const { data: notifications = [], refetch } = useQuery<Notification[]>(
    ['notifications'],
    fetchNotifications,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleNotificationClick = async (id: string) => {
    await markAsRead(id);
    refetch();
  };

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'competitor':
        return <TrendingUp color="primary" />;
      case 'battlecard':
        return <Description color="secondary" />;
      case 'marketing':
        return <Campaign color="action" />;
      case 'feature':
        return <Build color="success" />;
      default:
        return <NotificationsIcon />;
    }
  };

  const getTypeLabel = (type: Notification['type']) => {
    switch (type) {
      case 'competitor':
        return 'Competitor Update';
      case 'battlecard':
        return 'Battlecard';
      case 'marketing':
        return 'Marketing';
      case 'feature':
        return 'Feature Update';
      default:
        return type;
    }
  };

  return (
    <>
      <IconButton color="inherit" onClick={handleOpen}>
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Drawer
        anchor="right"
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 400 } },
        }}
      >
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Notifications
            {unreadCount > 0 && (
              <Chip
                label={`${unreadCount} new`}
                color="error"
                size="small"
                sx={{ ml: 1 }}
              />
            )}
          </Typography>
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider />
        <List sx={{ pt: 0 }}>
          {notifications.length === 0 ? (
            <ListItem>
              <ListItemText
                primary="No notifications"
                secondary="You're all caught up!"
              />
            </ListItem>
          ) : (
            notifications.map((notification) => (
              <React.Fragment key={notification.id}>
                <ListItem
                  button
                  onClick={() => handleNotificationClick(notification.id)}
                  sx={{
                    bgcolor: notification.read ? 'transparent' : 'action.hover',
                  }}
                >
                  <ListItemIcon>{getIcon(notification.type)}</ListItemIcon>
                  <ListItemText
                    primary={notification.title}
                    secondary={
                      <>
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.primary"
                        >
                          {getTypeLabel(notification.type)}
                        </Typography>
                        {" — "}
                        {notification.message}
                        <Typography
                          component="div"
                          variant="caption"
                          color="text.secondary"
                          sx={{ mt: 0.5 }}
                        >
                          {new Date(notification.timestamp).toLocaleString()}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                <Divider component="li" />
              </React.Fragment>
            ))
          )}
        </List>
      </Drawer>
    </>
  );
};

export default NotificationCenter; 
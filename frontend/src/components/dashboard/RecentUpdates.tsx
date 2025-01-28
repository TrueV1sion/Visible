import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Paper,
  Divider
} from '@mui/material';
import {
  Update as UpdateIcon,
  TrendingUp,
  Campaign,
  Build
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { fetchRecentUpdates } from '../../api/updates';

interface Update {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  type: 'feature' | 'competitor' | 'marketing' | 'product';
}

interface RecentUpdatesProps {
  type: 'marketing' | 'product' | 'sales';
}

const RecentUpdates: React.FC<RecentUpdatesProps> = ({ type }) => {
  const { data: updates, isLoading, error } = useQuery<Update[]>(
    ['updates', type],
    () => fetchRecentUpdates(type)
  );

  const getIcon = (updateType: Update['type']) => {
    switch (updateType) {
      case 'feature':
        return <Build />;
      case 'competitor':
        return <TrendingUp />;
      case 'marketing':
        return <Campaign />;
      default:
        return <UpdateIcon />;
    }
  };

  if (isLoading) {
    return <Typography>Loading updates...</Typography>;
  }

  if (error) {
    return <Typography color="error">Error loading updates</Typography>;
  }

  return (
    <Paper elevation={0}>
      <Typography variant="h6" gutterBottom>
        Recent Updates
      </Typography>
      <List>
        {updates?.map((update, index) => (
          <React.Fragment key={update.id}>
            <ListItem alignItems="flex-start">
              <ListItemIcon>
                {getIcon(update.type)}
              </ListItemIcon>
              <ListItemText
                primary={update.title}
                secondary={
                  <>
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.primary"
                    >
                      {new Date(update.timestamp).toLocaleDateString()}
                    </Typography>
                    {" — "}{update.description}
                  </>
                }
              />
            </ListItem>
            {index < updates.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default RecentUpdates; 
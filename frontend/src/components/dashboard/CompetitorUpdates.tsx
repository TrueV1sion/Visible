import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  IconButton,
  Typography,
  useTheme,
  useMediaQuery,
  Collapse,
  Button,
  Tooltip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as NeutralIcon,
  ExpandMore as ExpandMoreIcon,
  AutoAwesome as AIIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { fetchCompetitorUpdates, CompetitorUpdate } from '../../api/competitors';

const impactColors = {
  high: 'error',
  medium: 'warning',
  low: 'success',
  neutral: 'default',
} as const;

const impactIcons = {
  high: <TrendingUpIcon />,
  medium: <TrendingUpIcon />,
  low: <TrendingDownIcon />,
  neutral: <NeutralIcon />,
} as const;

const CompetitorUpdates: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const { data: updates = [], isLoading } = useQuery(
    ['competitorUpdates'],
    fetchCompetitorUpdates,
    {
      refetchInterval: 300000, // Refetch every 5 minutes
    }
  );

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const renderUpdateCard = (update: CompetitorUpdate) => {
    const isExpanded = expandedIds.has(update.id);

    return (
      <Card
        key={update.id}
        sx={{
          mb: 2,
          borderLeft: 6,
          borderColor: `${theme.palette[impactColors[update.impact]].main}`,
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Chip
                label={update.competitor}
                variant="outlined"
                size="small"
                sx={{ mr: 1 }}
              />
              <Chip
                label={update.type}
                size="small"
                sx={{ mr: 1 }}
              />
              <Tooltip title={`Impact: ${update.impact}`}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {impactIcons[update.impact]}
                </Box>
              </Tooltip>
            </Box>
            <Typography variant="caption" color="text.secondary">
              {new Date(update.timestamp).toLocaleDateString()}
            </Typography>
          </Box>

          <Typography variant="subtitle1" gutterBottom>
            {update.title}
          </Typography>

          <Collapse in={isExpanded}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" paragraph>
                {update.description}
              </Typography>

              {update.aiInsights && (
                <Alert
                  icon={<AIIcon />}
                  severity="info"
                  sx={{
                    mt: 2,
                    '& .MuiAlert-message': {
                      width: '100%',
                    },
                  }}
                >
                  <Typography variant="subtitle2" gutterBottom>
                    AI Insights
                  </Typography>
                  <Typography variant="body2">
                    {update.aiInsights}
                  </Typography>
                  <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                    {update.suggestedActions?.map((action, index) => (
                      <Chip
                        key={index}
                        label={action}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Alert>
              )}

              {update.sources && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Sources:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 0.5 }}>
                    {update.sources.map((source, index) => (
                      <Chip
                        key={index}
                        label={source}
                        size="small"
                        variant="outlined"
                        onClick={() => window.open(source, '_blank')}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>
          </Collapse>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Button
              size="small"
              onClick={() => toggleExpand(update.id)}
              endIcon={
                <ExpandMoreIcon
                  sx={{
                    transform: isExpanded ? 'rotate(180deg)' : 'rotate(0)',
                    transition: theme.transitions.create('transform'),
                  }}
                />
              }
            >
              {isExpanded ? 'Show Less' : 'Show More'}
            </Button>
            {!isMobile && (
              <Tooltip title="View related battlecards">
                <Button size="small" startIcon={<InfoIcon />}>
                  Related Cards
                </Button>
              </Tooltip>
            )}
          </Box>
        </CardContent>
      </Card>
    );
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {updates.length === 0 ? (
        <Alert severity="info">No recent competitor updates</Alert>
      ) : (
        updates.map(renderUpdateCard)
      )}
    </Box>
  );
};

export default CompetitorUpdates; 
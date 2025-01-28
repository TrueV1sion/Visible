import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  AlertTitle,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
  Collapse,
  Button,
} from '@mui/material';
import {
  AutoAwesome as AIIcon,
  Lightbulb as InsightIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Check as ApplyIcon,
  Close as DiscardIcon,
} from '@mui/icons-material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { generateInsights, applyInsight, InsightType } from '../../api/insights';

interface InsightSuggestion {
  id: string;
  type: InsightType;
  content: string;
  confidence: number;
  sources: string[];
  suggestedActions: string[];
  timestamp: string;
}

interface InsightsGenerationAgentProps {
  context: {
    battlecardId?: string;
    competitorId?: string;
    productId?: string;
    section?: string;
  };
  onInsightApply?: (insight: InsightSuggestion) => void;
  onInsightDiscard?: (insightId: string) => void;
}

const InsightsGenerationAgent: React.FC<InsightsGenerationAgentProps> = ({
  context,
  onInsightApply,
  onInsightDiscard,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [expandedInsights, setExpandedInsights] = useState<Set<string>>(new Set());

  const { data: insights = [], isLoading, error } = useQuery(
    ['insights', context],
    () => generateInsights(context),
    {
      enabled: !!context,
      refetchInterval: 60000, // Refresh every minute
    }
  );

  const applyMutation = useMutation(applyInsight, {
    onSuccess: (_, insight) => {
      onInsightApply?.(insight);
    },
  });

  const toggleExpand = (id: string) => {
    setExpandedInsights((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const renderInsightCard = (insight: InsightSuggestion) => {
    const isExpanded = expandedInsights.has(insight.id);

    return (
      <Card
        key={insight.id}
        sx={{
          mb: 2,
          borderLeft: 6,
          borderColor: theme.palette[getConfidenceColor(insight.confidence)].main,
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AIIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="subtitle1">
                AI-Generated Insight
              </Typography>
            </Box>
            <Box>
              <Chip
                label={`${(insight.confidence * 100).toFixed(0)}% Confidence`}
                color={getConfidenceColor(insight.confidence)}
                size="small"
                sx={{ mr: 1 }}
              />
              <Chip
                label={insight.type}
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>

          <Typography variant="body1" gutterBottom>
            {insight.content}
          </Typography>

          <Collapse in={isExpanded}>
            <Box sx={{ mt: 2 }}>
              {insight.suggestedActions.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Suggested Actions:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {insight.suggestedActions.map((action, index) => (
                      <Chip
                        key={index}
                        label={action}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {insight.sources.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Sources:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {insight.sources.map((source, index) => (
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

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <Button
              size="small"
              onClick={() => toggleExpand(insight.id)}
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
            <Box>
              <Tooltip title="Discard this insight">
                <IconButton
                  size="small"
                  onClick={() => onInsightDiscard?.(insight.id)}
                  sx={{ mr: 1 }}
                >
                  <DiscardIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Apply this insight">
                <IconButton
                  size="small"
                  onClick={() => applyMutation.mutate(insight)}
                  color="primary"
                >
                  <ApplyIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4 }}>
        <CircularProgress size={24} sx={{ mr: 2 }} />
        <Typography>Generating insights...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        <AlertTitle>Error</AlertTitle>
        Failed to generate insights. Please try again later.
      </Alert>
    );
  }

  return (
    <Box>
      {insights.length === 0 ? (
        <Alert severity="info">
          No insights available for the current context.
        </Alert>
      ) : (
        insights.map(renderInsightCard)
      )}
    </Box>
  );
};

export default InsightsGenerationAgent; 
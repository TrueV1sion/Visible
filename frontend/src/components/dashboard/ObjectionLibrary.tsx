import React, { useState, ChangeEvent, MouseEvent } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Collapse,
  IconButton,
  TextField,
  InputAdornment,
  Paper
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  Search,
  ThumbUp,
  ThumbDown
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { fetchObjections, Objection } from '../../api/objections';

const ObjectionLibrary: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: objections, isLoading, error } = useQuery<Objection[]>(
    ['objections'],
    fetchObjections
  );

  const handleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const filteredObjections = objections?.filter((obj: Objection) =>
    obj.objection.toLowerCase().includes(searchTerm.toLowerCase()) ||
    obj.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getEffectivenessColor = (effectiveness: number) => {
    if (effectiveness >= 80) return 'success.main';
    if (effectiveness >= 60) return 'warning.main';
    return 'error.main';
  };

  if (isLoading) {
    return <Typography>Loading objection library...</Typography>;
  }

  if (error) {
    return <Typography color="error">Error loading objections</Typography>;
  }

  return (
    <Paper elevation={0}>
      <Box p={2}>
        <Typography variant="h6" gutterBottom>
          Common Objections
        </Typography>
        <TextField
          fullWidth
          size="small"
          placeholder="Search objections..."
          value={searchTerm}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
          sx={{ mb: 2 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
        <List>
          {filteredObjections?.map((obj: Objection) => (
            <React.Fragment key={obj.id}>
              <ListItem
                button
                onClick={() => handleExpand(obj.id)}
                sx={{
                  borderRadius: 1,
                  mb: 1,
                  bgcolor: 'background.paper',
                }}
              >
                <ListItemText
                  primary={obj.objection}
                  secondary={obj.category}
                />
                <Box display="flex" alignItems="center">
                  {obj.effectiveness >= 70 ? (
                    <ThumbUp color="success" sx={{ mr: 1 }} />
                  ) : (
                    <ThumbDown color="error" sx={{ mr: 1 }} />
                  )}
                  <Typography
                    variant="body2"
                    color={getEffectivenessColor(obj.effectiveness)}
                    sx={{ mr: 2 }}
                  >
                    {obj.effectiveness}%
                  </Typography>
                  <IconButton
                    edge="end"
                    size="small"
                    onClick={(e: MouseEvent) => {
                      e.stopPropagation();
                      handleExpand(obj.id);
                    }}
                  >
                    {expandedId === obj.id ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>
              </ListItem>
              <Collapse in={expandedId === obj.id} timeout="auto" unmountOnExit>
                <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1, mb: 1 }}>
                  <Typography variant="body1" gutterBottom>
                    Recommended Response:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {obj.response}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Used {obj.usageCount} times
                  </Typography>
                </Box>
              </Collapse>
            </React.Fragment>
          ))}
        </List>
      </Box>
    </Paper>
  );
};

export default ObjectionLibrary; 
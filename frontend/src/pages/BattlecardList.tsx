import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';

interface Battlecard {
  id: string;
  title: string;
  competitor: string;
  lastUpdated: string;
  status: 'draft' | 'published' | 'archived';
  tags: string[];
}

const BattlecardList: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
  const [actionAnchorEl, setActionAnchorEl] = useState<{
    [key: string]: HTMLElement | null;
  }>({});

  // Mock data - replace with API call
  const battlecards: Battlecard[] = [
    {
      id: '1',
      title: 'Competitor X Enterprise Solution',
      competitor: 'Competitor X',
      lastUpdated: '2024-03-15',
      status: 'published',
      tags: ['Enterprise', 'Cloud'],
    },
    {
      id: '2',
      title: 'Competitor Y SMB Offering',
      competitor: 'Competitor Y',
      lastUpdated: '2024-03-14',
      status: 'draft',
      tags: ['SMB', 'On-premise'],
    },
    // Add more mock data as needed
  ];

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleStatusSelect = (status: string | null) => {
    setSelectedStatus(status);
    handleFilterClose();
  };

  const handleActionClick = (
    event: React.MouseEvent<HTMLElement>,
    cardId: string
  ) => {
    setActionAnchorEl({
      ...actionAnchorEl,
      [cardId]: event.currentTarget,
    });
  };

  const handleActionClose = (cardId: string) => {
    setActionAnchorEl({
      ...actionAnchorEl,
      [cardId]: null,
    });
  };

  const filteredBattlecards = battlecards
    .filter((card) =>
      card.title.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .filter(
      (card) => !selectedStatus || card.status === selectedStatus.toLowerCase()
    );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'success';
      case 'draft':
        return 'warning';
      case 'archived':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h4">Battlecards</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/battlecards/new')}
        >
          Create Battlecard
        </Button>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              placeholder="Search battlecards..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={handleFilterClick}
            >
              {selectedStatus || 'Filter by Status'}
            </Button>
            <Menu
              anchorEl={filterAnchorEl}
              open={Boolean(filterAnchorEl)}
              onClose={handleFilterClose}
            >
              <MenuItem onClick={() => handleStatusSelect(null)}>All</MenuItem>
              <MenuItem onClick={() => handleStatusSelect('Published')}>
                Published
              </MenuItem>
              <MenuItem onClick={() => handleStatusSelect('Draft')}>
                Draft
              </MenuItem>
              <MenuItem onClick={() => handleStatusSelect('Archived')}>
                Archived
              </MenuItem>
            </Menu>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={3}>
        {filteredBattlecards.map((card) => (
          <Grid item xs={12} key={card.id}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                  }}
                >
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {card.title}
                    </Typography>
                    <Typography
                      variant="subtitle2"
                      color="text.secondary"
                      gutterBottom
                    >
                      {card.competitor}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        label={card.status}
                        size="small"
                        color={getStatusColor(card.status)}
                        sx={{ mr: 1 }}
                      />
                      {card.tags.map((tag) => (
                        <Chip
                          key={tag}
                          label={tag}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 1 }}
                        />
                      ))}
                    </Box>
                  </Box>
                  <Box>
                    <IconButton
                      onClick={(e) => handleActionClick(e, card.id)}
                      size="small"
                    >
                      <MoreVertIcon />
                    </IconButton>
                    <Menu
                      anchorEl={actionAnchorEl[card.id]}
                      open={Boolean(actionAnchorEl[card.id])}
                      onClose={() => handleActionClose(card.id)}
                    >
                      <MenuItem
                        onClick={() => navigate(`/battlecards/${card.id}/edit`)}
                      >
                        <EditIcon sx={{ mr: 1 }} /> Edit
                      </MenuItem>
                      <MenuItem onClick={() => handleActionClose(card.id)}>
                        <DeleteIcon sx={{ mr: 1 }} /> Delete
                      </MenuItem>
                    </Menu>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default BattlecardList; 
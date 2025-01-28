import React, { useState, useCallback } from 'react';
import {
  Box,
  TextField,
  Autocomplete,
  Chip,
  IconButton,
  InputAdornment,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useQuery, useMutation } from '@tanstack/react-query';
import debounce from 'lodash/debounce';
import { searchBattlecards, SearchFilters, SearchResult } from '../../api/search';

interface AdvancedSearchProps {
  onResultSelect: (result: SearchResult) => void;
}

const productLines = [
  'Enterprise',
  'Small Business',
  'Consumer',
  'Government',
  'Healthcare',
];

const competitors = [
  'Competitor A',
  'Competitor B',
  'Competitor C',
  'Competitor D',
];

const AdvancedSearch: React.FC<AdvancedSearchProps> = ({ onResultSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    productLines: [],
    competitors: [],
    dateRange: 'all',
    type: 'all',
  });

  const { data: results = [], isLoading } = useQuery(
    ['search', searchQuery, filters],
    () => searchBattlecards(searchQuery, filters),
    {
      enabled: searchQuery.length > 2,
    }
  );

  const debouncedSearch = useCallback(
    debounce((value: string) => {
      setSearchQuery(value);
    }, 300),
    []
  );

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    debouncedSearch(event.target.value);
  };

  const handleFilterChange = (field: keyof SearchFilters, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const clearFilters = () => {
    setFilters({
      productLines: [],
      competitors: [],
      dateRange: 'all',
      type: 'all',
    });
  };

  return (
    <Box>
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TextField
            fullWidth
            placeholder="Search battlecards, competitors, or ask a question..."
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowFilters(!showFilters)}
                    color={showFilters ? 'primary' : 'default'}
                  >
                    <FilterIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {showFilters && (
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  multiple
                  options={productLines}
                  value={filters.productLines}
                  onChange={(_, newValue) =>
                    handleFilterChange('productLines', newValue)
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Product Lines"
                      placeholder="Select product lines"
                    />
                  )}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        label={option}
                        {...getTagProps({ index })}
                        key={option}
                      />
                    ))
                  }
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  multiple
                  options={competitors}
                  value={filters.competitors}
                  onChange={(_, newValue) =>
                    handleFilterChange('competitors', newValue)
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Competitors"
                      placeholder="Select competitors"
                    />
                  )}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        label={option}
                        {...getTagProps({ index })}
                        key={option}
                      />
                    ))
                  }
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Date Range</InputLabel>
                  <Select
                    value={filters.dateRange}
                    label="Date Range"
                    onChange={(e) =>
                      handleFilterChange('dateRange', e.target.value)
                    }
                  >
                    <MenuItem value="all">All Time</MenuItem>
                    <MenuItem value="week">Past Week</MenuItem>
                    <MenuItem value="month">Past Month</MenuItem>
                    <MenuItem value="quarter">Past Quarter</MenuItem>
                    <MenuItem value="year">Past Year</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Content Type</InputLabel>
                  <Select
                    value={filters.type}
                    label="Content Type"
                    onChange={(e) => handleFilterChange('type', e.target.value)}
                  >
                    <MenuItem value="all">All Types</MenuItem>
                    <MenuItem value="battlecard">Battlecards</MenuItem>
                    <MenuItem value="competitor">Competitor Updates</MenuItem>
                    <MenuItem value="objection">Objection Handling</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={clearFilters} sx={{ mr: 1 }}>
                Clear Filters
              </Button>
            </Box>
          </Box>
        )}
      </Paper>

      {/* Search Results */}
      <Box>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          results.map((result) => (
            <Paper
              key={result.id}
              sx={{
                p: 2,
                mb: 2,
                cursor: 'pointer',
                '&:hover': { bgcolor: 'action.hover' },
              }}
              onClick={() => onResultSelect(result)}
            >
              <Typography variant="h6" gutterBottom>
                {result.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {result.excerpt}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Chip
                  label={result.type}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
                {result.tags.map((tag) => (
                  <Chip key={tag} label={tag} size="small" />
                ))}
              </Box>
            </Paper>
          ))
        )}
      </Box>
    </Box>
  );
};

export default AdvancedSearch; 
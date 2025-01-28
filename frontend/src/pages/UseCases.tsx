import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  AutoAwesome as AutoAwesomeIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

interface UseCase {
  id: string;
  title: string;
  industry: string;
  challenge: string;
  solution: string;
  results: string[];
  tags: string[];
}

interface UseCaseFormData {
  title: string;
  industry: string;
  challenge: string;
  solution: string;
  results: string[];
  tags: string[];
}

const UseCases: React.FC = () => {
  const [useCases, setUseCases] = useState<UseCase[]>([
    {
      id: '1',
      title: 'Enterprise Customer Success Story',
      industry: 'Technology',
      challenge:
        'A large enterprise customer needed to streamline their operations...',
      solution:
        'We implemented our platform with custom integrations to address...',
      results: [
        '50% reduction in processing time',
        '30% cost savings',
        'Improved customer satisfaction',
      ],
      tags: ['Enterprise', 'Integration', 'Automation'],
    },
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUseCase, setEditingUseCase] = useState<UseCase | null>(null);
  const [formData, setFormData] = useState<UseCaseFormData>({
    title: '',
    industry: '',
    challenge: '',
    solution: '',
    results: [''],
    tags: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const industries = [
    'Technology',
    'Healthcare',
    'Finance',
    'Manufacturing',
    'Retail',
    'Other',
  ];

  const handleOpenDialog = (useCase?: UseCase) => {
    if (useCase) {
      setEditingUseCase(useCase);
      setFormData({
        title: useCase.title,
        industry: useCase.industry,
        challenge: useCase.challenge,
        solution: useCase.solution,
        results: useCase.results,
        tags: useCase.tags,
      });
    } else {
      setEditingUseCase(null);
      setFormData({
        title: '',
        industry: '',
        challenge: '',
        solution: '',
        results: [''],
        tags: [],
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingUseCase(null);
    setFormData({
      title: '',
      industry: '',
      challenge: '',
      solution: '',
      results: [''],
      tags: [],
    });
  };

  const handleSave = () => {
    if (
      !formData.title ||
      !formData.industry ||
      !formData.challenge ||
      !formData.solution ||
      formData.results.length === 0
    ) {
      setError('Please fill in all required fields');
      return;
    }

    if (editingUseCase) {
      setUseCases(
        useCases.map((uc) =>
          uc.id === editingUseCase.id
            ? { ...uc, ...formData }
            : uc
        )
      );
    } else {
      const newUseCase: UseCase = {
        id: Date.now().toString(),
        ...formData,
      };
      setUseCases([...useCases, newUseCase]);
    }

    handleCloseDialog();
  };

  const handleDelete = (id: string) => {
    setUseCases(useCases.filter((uc) => uc.id !== id));
  };

  const handleResultAdd = () => {
    setFormData({
      ...formData,
      results: [...formData.results, ''],
    });
  };

  const handleResultRemove = (index: number) => {
    const newResults = [...formData.results];
    newResults.splice(index, 1);
    setFormData({
      ...formData,
      results: newResults,
    });
  };

  const handleTagAdd = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      const input = event.target as HTMLInputElement;
      const value = input.value.trim();
      if (value && !formData.tags.includes(value)) {
        setFormData({
          ...formData,
          tags: [...formData.tags, value],
        });
        input.value = '';
      }
    }
  };

  const handleTagDelete = (tagToDelete: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter((tag) => tag !== tagToDelete),
    });
  };

  const handleGenerateContent = async (field: 'challenge' | 'solution') => {
    if (field === 'solution' && !formData.challenge) {
      setError('Please enter the challenge first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Mock API call - replace with actual AI integration
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      const generatedContent =
        field === 'challenge'
          ? 'Based on our analysis, here is a detailed description of the customer challenge...'
          : 'Here is a comprehensive solution that addresses the specified challenge...';

      setFormData({
        ...formData,
        [field]: generatedContent,
      });
    } catch (error) {
      setError('Failed to generate content. Please try again.');
      console.error('Generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredUseCases = useCases
    .filter((uc) =>
      uc.title.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .filter((uc) => !selectedIndustry || uc.industry === selectedIndustry);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Use Cases
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Search use cases"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title..."
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {industries.map((industry) => (
                  <Chip
                    key={industry}
                    label={industry}
                    onClick={() =>
                      setSelectedIndustry(
                        selectedIndustry === industry ? null : industry
                      )
                    }
                    color={selectedIndustry === industry ? 'primary' : 'default'}
                  />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => handleOpenDialog()}
              >
                Add New
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {filteredUseCases.map((useCase) => (
          <Grid item xs={12} key={useCase.id}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                  }}
                >
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {useCase.title}
                    </Typography>
                    <Typography variant="subtitle1" color="text.secondary">
                      Industry: {useCase.industry}
                    </Typography>
                    <Typography variant="body1" sx={{ mt: 2 }}>
                      <strong>Challenge:</strong> {useCase.challenge}
                    </Typography>
                    <Typography variant="body1" sx={{ mt: 2 }}>
                      <strong>Solution:</strong> {useCase.solution}
                    </Typography>
                    <Typography variant="body1" sx={{ mt: 2 }}>
                      <strong>Results:</strong>
                    </Typography>
                    <Box component="ul" sx={{ mt: 1 }}>
                      {useCase.results.map((result, index) => (
                        <Typography component="li" key={index}>
                          {result}
                        </Typography>
                      ))}
                    </Box>
                    <Box sx={{ mt: 2 }}>
                      {useCase.tags.map((tag) => (
                        <Chip
                          key={tag}
                          label={tag}
                          variant="outlined"
                          size="small"
                          sx={{ mr: 1 }}
                        />
                      ))}
                    </Box>
                  </Box>
                  <Box>
                    <IconButton
                      onClick={() => handleOpenDialog(useCase)}
                      size="small"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => handleDelete(useCase.id)}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingUseCase ? 'Edit Use Case' : 'Add New Use Case'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                select
                label="Industry"
                value={formData.industry}
                onChange={(e) =>
                  setFormData({ ...formData, industry: e.target.value })
                }
                required
                SelectProps={{
                  native: true,
                }}
              >
                <option value="">Select an industry</option>
                {industries.map((industry) => (
                  <option key={industry} value={industry}>
                    {industry}
                  </option>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Challenge"
                  multiline
                  rows={4}
                  value={formData.challenge}
                  onChange={(e) =>
                    setFormData({ ...formData, challenge: e.target.value })
                  }
                  required
                />
                <Button
                  variant="outlined"
                  onClick={() => handleGenerateContent('challenge')}
                  disabled={loading}
                  startIcon={
                    loading ? (
                      <CircularProgress size={20} />
                    ) : (
                      <AutoAwesomeIcon />
                    )
                  }
                >
                  Generate
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Solution"
                  multiline
                  rows={4}
                  value={formData.solution}
                  onChange={(e) =>
                    setFormData({ ...formData, solution: e.target.value })
                  }
                  required
                />
                <Button
                  variant="outlined"
                  onClick={() => handleGenerateContent('solution')}
                  disabled={loading}
                  startIcon={
                    loading ? (
                      <CircularProgress size={20} />
                    ) : (
                      <AutoAwesomeIcon />
                    )
                  }
                >
                  Generate
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 2,
                }}
              >
                <Typography variant="subtitle1">Results</Typography>
                <Button
                  startIcon={<AddIcon />}
                  onClick={handleResultAdd}
                  size="small"
                >
                  Add Result
                </Button>
              </Box>
              {formData.results.map((result, index) => (
                <Box key={index} sx={{ display: 'flex', mb: 2 }}>
                  <TextField
                    fullWidth
                    label={`Result ${index + 1}`}
                    value={result}
                    onChange={(e) => {
                      const newResults = [...formData.results];
                      newResults[index] = e.target.value;
                      setFormData({
                        ...formData,
                        results: newResults,
                      });
                    }}
                    required
                  />
                  <IconButton
                    onClick={() => handleResultRemove(index)}
                    disabled={formData.results.length === 1}
                    sx={{ ml: 1 }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ mb: 2 }}>
                {formData.tags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    onDelete={() => handleTagDelete(tag)}
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
              <TextField
                fullWidth
                label="Add tags (press Enter)"
                onKeyDown={handleTagAdd}
              />
            </Grid>
          </Grid>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UseCases; 
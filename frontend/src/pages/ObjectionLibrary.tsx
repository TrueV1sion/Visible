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

interface Objection {
  id: string;
  objection: string;
  response: string;
  category: string;
  tags: string[];
}

interface ObjectionFormData {
  objection: string;
  response: string;
  category: string;
  tags: string[];
}

const ObjectionLibrary: React.FC = () => {
  const [objections, setObjections] = useState<Objection[]>([
    {
      id: '1',
      objection: 'Your product is too expensive',
      response:
        'While our pricing may be higher initially, our solution provides superior ROI through...',
      category: 'Pricing',
      tags: ['Price', 'Value', 'ROI'],
    },
    {
      id: '2',
      objection: 'We already have a solution',
      response:
        'I understand you have an existing solution. Let me highlight some key differentiators...',
      category: 'Competition',
      tags: ['Existing Customer', 'Migration'],
    },
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingObjection, setEditingObjection] = useState<Objection | null>(
    null
  );
  const [formData, setFormData] = useState<ObjectionFormData>({
    objection: '',
    response: '',
    category: '',
    tags: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const categories = [
    'Pricing',
    'Competition',
    'Technical',
    'Implementation',
    'Security',
    'Other',
  ];

  const handleOpenDialog = (objection?: Objection) => {
    if (objection) {
      setEditingObjection(objection);
      setFormData({
        objection: objection.objection,
        response: objection.response,
        category: objection.category,
        tags: objection.tags,
      });
    } else {
      setEditingObjection(null);
      setFormData({
        objection: '',
        response: '',
        category: '',
        tags: [],
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingObjection(null);
    setFormData({
      objection: '',
      response: '',
      category: '',
      tags: [],
    });
  };

  const handleSave = () => {
    if (!formData.objection || !formData.response || !formData.category) {
      setError('Please fill in all required fields');
      return;
    }

    if (editingObjection) {
      setObjections(
        objections.map((obj) =>
          obj.id === editingObjection.id
            ? { ...obj, ...formData }
            : obj
        )
      );
    } else {
      const newObjection: Objection = {
        id: Date.now().toString(),
        ...formData,
      };
      setObjections([...objections, newObjection]);
    }

    handleCloseDialog();
  };

  const handleDelete = (id: string) => {
    setObjections(objections.filter((obj) => obj.id !== id));
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

  const handleGenerateResponse = async () => {
    if (!formData.objection) {
      setError('Please enter an objection first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Mock API call - replace with actual AI integration
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      setFormData({
        ...formData,
        response:
          'Based on our analysis, here is a suggested response to handle this objection effectively...',
      });
    } catch (error) {
      setError('Failed to generate response. Please try again.');
      console.error('Generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredObjections = objections
    .filter((obj) =>
      obj.objection.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .filter((obj) => !selectedCategory || obj.category === selectedCategory);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Objection Library
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Search objections"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by objection text..."
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {categories.map((category) => (
                  <Chip
                    key={category}
                    label={category}
                    onClick={() =>
                      setSelectedCategory(
                        selectedCategory === category ? null : category
                      )
                    }
                    color={selectedCategory === category ? 'primary' : 'default'}
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
        {filteredObjections.map((obj) => (
          <Grid item xs={12} key={obj.id}>
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
                      {obj.objection}
                    </Typography>
                    <Typography
                      variant="body1"
                      color="text.secondary"
                      paragraph
                    >
                      {obj.response}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Chip
                        label={obj.category}
                        color="primary"
                        sx={{ mr: 1 }}
                      />
                      {obj.tags.map((tag) => (
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
                      onClick={() => handleOpenDialog(obj)}
                      size="small"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => handleDelete(obj.id)}
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
          {editingObjection ? 'Edit Objection' : 'Add New Objection'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Objection"
                value={formData.objection}
                onChange={(e) =>
                  setFormData({ ...formData, objection: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Response"
                  multiline
                  rows={4}
                  value={formData.response}
                  onChange={(e) =>
                    setFormData({ ...formData, response: e.target.value })
                  }
                  required
                />
                <Button
                  variant="outlined"
                  onClick={handleGenerateResponse}
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
              <TextField
                fullWidth
                select
                label="Category"
                value={formData.category}
                onChange={(e) =>
                  setFormData({ ...formData, category: e.target.value })
                }
                required
                SelectProps={{
                  native: true,
                }}
              >
                <option value="">Select a category</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </TextField>
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

export default ObjectionLibrary; 
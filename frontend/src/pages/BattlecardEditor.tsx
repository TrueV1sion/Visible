import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useFormik } from 'formik';
import * as yup from 'yup';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  TextField,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material';
import {
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  AutoAwesome as AutoAwesomeIcon,
} from '@mui/icons-material';

const validationSchema = yup.object({
  title: yup.string().required('Title is required'),
  competitor: yup.string().required('Competitor name is required'),
  overview: yup.string().required('Overview is required'),
  strengths: yup.array().of(yup.string()).min(1, 'At least one strength is required'),
  weaknesses: yup.array().of(yup.string()).min(1, 'At least one weakness is required'),
  competitiveAdvantages: yup
    .array()
    .of(yup.string())
    .min(1, 'At least one competitive advantage is required'),
  ourPricing: yup.string().required('Our pricing is required'),
  theirPricing: yup.string().required('Their pricing is required'),
  pricingAnalysis: yup.string().required('Pricing analysis is required'),
  objections: yup
    .array()
    .of(
      yup.object({
        objection: yup.string().required('Objection is required'),
        response: yup.string().required('Response is required'),
      })
    )
    .min(1, 'At least one objection is required'),
  winningStrategies: yup
    .array()
    .of(yup.string())
    .min(1, 'At least one winning strategy is required'),
  tags: yup.array().of(yup.string()).min(1, 'At least one tag is required'),
});

interface AIGenerationDialogProps {
  open: boolean;
  onClose: () => void;
  onGenerate: (field: string) => void;
  loading: boolean;
}

const AIGenerationDialog: React.FC<AIGenerationDialogProps> = ({
  open,
  onClose,
  onGenerate,
  loading,
}) => {
  const fields = [
    'Overview',
    'Strengths & Weaknesses',
    'Competitive Advantages',
    'Pricing Analysis',
    'Objection Responses',
    'Winning Strategies',
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Generate Content with AI</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Select a section to generate content using AI analysis
        </Typography>
        <Grid container spacing={2}>
          {fields.map((field) => (
            <Grid item xs={12} sm={6} key={field}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => onGenerate(field)}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesomeIcon />}
              >
                {field}
              </Button>
            </Grid>
          ))}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

const BattlecardEditor: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [aiDialogOpen, setAiDialogOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);

  const formik = useFormik({
    initialValues: {
      title: '',
      competitor: '',
      overview: '',
      strengths: [''],
      weaknesses: [''],
      competitiveAdvantages: [''],
      ourPricing: '',
      theirPricing: '',
      pricingAnalysis: '',
      objections: [{ objection: '', response: '' }],
      winningStrategies: [''],
      tags: [],
      status: 'draft',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        // API call to save battlecard
        console.log('Saving battlecard:', values);
        navigate('/battlecards');
      } catch (error) {
        console.error('Error saving battlecard:', error);
      }
    },
  });

  const handleArrayFieldAdd = (field: string) => {
    const values = [...formik.values[field]];
    values.push('');
    formik.setFieldValue(field, values);
  };

  const handleArrayFieldRemove = (field: string, index: number) => {
    const values = [...formik.values[field]];
    values.splice(index, 1);
    formik.setFieldValue(field, values);
  };

  const handleObjectionAdd = () => {
    const objections = [...formik.values.objections];
    objections.push({ objection: '', response: '' });
    formik.setFieldValue('objections', objections);
  };

  const handleObjectionRemove = (index: number) => {
    const objections = [...formik.values.objections];
    objections.splice(index, 1);
    formik.setFieldValue('objections', objections);
  };

  const handleTagAdd = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      const input = event.target as HTMLInputElement;
      const value = input.value.trim();
      if (value && !formik.values.tags.includes(value)) {
        formik.setFieldValue('tags', [...formik.values.tags, value]);
        input.value = '';
      }
    }
  };

  const handleTagDelete = (tagToDelete: string) => {
    formik.setFieldValue(
      'tags',
      formik.values.tags.filter((tag) => tag !== tagToDelete)
    );
  };

  const handleAIGenerate = async (field: string) => {
    setAiLoading(true);
    try {
      // API call to generate content
      await new Promise((resolve) => setTimeout(resolve, 2000)); // Mock API delay
      console.log('Generating content for:', field);
      // Update form with generated content
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setAiLoading(false);
      setAiDialogOpen(false);
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
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/battlecards')}
        >
          Back to Battlecards
        </Button>
        <Box>
          <Button
            variant="outlined"
            startIcon={<AutoAwesomeIcon />}
            onClick={() => setAiDialogOpen(true)}
            sx={{ mr: 2 }}
          >
            AI Assist
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={() => formik.handleSubmit()}
          >
            Save
          </Button>
        </Box>
      </Box>

      <form onSubmit={formik.handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Basic Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Title"
                      name="title"
                      value={formik.values.title}
                      onChange={formik.handleChange}
                      error={formik.touched.title && Boolean(formik.errors.title)}
                      helperText={formik.touched.title && formik.errors.title}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Competitor"
                      name="competitor"
                      value={formik.values.competitor}
                      onChange={formik.handleChange}
                      error={
                        formik.touched.competitor &&
                        Boolean(formik.errors.competitor)
                      }
                      helperText={
                        formik.touched.competitor && formik.errors.competitor
                      }
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Overview"
                      name="overview"
                      multiline
                      rows={4}
                      value={formik.values.overview}
                      onChange={formik.handleChange}
                      error={
                        formik.touched.overview && Boolean(formik.errors.overview)
                      }
                      helperText={
                        formik.touched.overview && formik.errors.overview
                      }
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Tags
                </Typography>
                <Box sx={{ mb: 2 }}>
                  {formik.values.tags.map((tag) => (
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
                  error={formik.touched.tags && Boolean(formik.errors.tags)}
                  helperText={formik.touched.tags && formik.errors.tags}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Strengths & Weaknesses
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Strengths
                    </Typography>
                    {formik.values.strengths.map((strength, index) => (
                      <Box key={index} sx={{ display: 'flex', mb: 2 }}>
                        <TextField
                          fullWidth
                          label={`Strength ${index + 1}`}
                          value={strength}
                          onChange={(e) => {
                            const newStrengths = [...formik.values.strengths];
                            newStrengths[index] = e.target.value;
                            formik.setFieldValue('strengths', newStrengths);
                          }}
                          error={
                            formik.touched.strengths &&
                            Boolean(formik.errors.strengths)
                          }
                          helperText={
                            formik.touched.strengths && formik.errors.strengths
                          }
                        />
                        <IconButton
                          onClick={() => handleArrayFieldRemove('strengths', index)}
                          disabled={formik.values.strengths.length === 1}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    ))}
                    <Button
                      startIcon={<AddIcon />}
                      onClick={() => handleArrayFieldAdd('strengths')}
                    >
                      Add Strength
                    </Button>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Weaknesses
                    </Typography>
                    {formik.values.weaknesses.map((weakness, index) => (
                      <Box key={index} sx={{ display: 'flex', mb: 2 }}>
                        <TextField
                          fullWidth
                          label={`Weakness ${index + 1}`}
                          value={weakness}
                          onChange={(e) => {
                            const newWeaknesses = [...formik.values.weaknesses];
                            newWeaknesses[index] = e.target.value;
                            formik.setFieldValue('weaknesses', newWeaknesses);
                          }}
                          error={
                            formik.touched.weaknesses &&
                            Boolean(formik.errors.weaknesses)
                          }
                          helperText={
                            formik.touched.weaknesses && formik.errors.weaknesses
                          }
                        />
                        <IconButton
                          onClick={() =>
                            handleArrayFieldRemove('weaknesses', index)
                          }
                          disabled={formik.values.weaknesses.length === 1}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    ))}
                    <Button
                      startIcon={<AddIcon />}
                      onClick={() => handleArrayFieldAdd('weaknesses')}
                    >
                      Add Weakness
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Competitive Advantages
                </Typography>
                {formik.values.competitiveAdvantages.map((advantage, index) => (
                  <Box key={index} sx={{ display: 'flex', mb: 2 }}>
                    <TextField
                      fullWidth
                      label={`Advantage ${index + 1}`}
                      value={advantage}
                      onChange={(e) => {
                        const newAdvantages = [
                          ...formik.values.competitiveAdvantages,
                        ];
                        newAdvantages[index] = e.target.value;
                        formik.setFieldValue(
                          'competitiveAdvantages',
                          newAdvantages
                        );
                      }}
                      error={
                        formik.touched.competitiveAdvantages &&
                        Boolean(formik.errors.competitiveAdvantages)
                      }
                      helperText={
                        formik.touched.competitiveAdvantages &&
                        formik.errors.competitiveAdvantages
                      }
                    />
                    <IconButton
                      onClick={() =>
                        handleArrayFieldRemove('competitiveAdvantages', index)
                      }
                      disabled={formik.values.competitiveAdvantages.length === 1}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                ))}
                <Button
                  startIcon={<AddIcon />}
                  onClick={() => handleArrayFieldAdd('competitiveAdvantages')}
                >
                  Add Advantage
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Pricing
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Our Pricing"
                      name="ourPricing"
                      value={formik.values.ourPricing}
                      onChange={formik.handleChange}
                      error={
                        formik.touched.ourPricing &&
                        Boolean(formik.errors.ourPricing)
                      }
                      helperText={
                        formik.touched.ourPricing && formik.errors.ourPricing
                      }
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Their Pricing"
                      name="theirPricing"
                      value={formik.values.theirPricing}
                      onChange={formik.handleChange}
                      error={
                        formik.touched.theirPricing &&
                        Boolean(formik.errors.theirPricing)
                      }
                      helperText={
                        formik.touched.theirPricing && formik.errors.theirPricing
                      }
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Pricing Analysis"
                      name="pricingAnalysis"
                      multiline
                      rows={4}
                      value={formik.values.pricingAnalysis}
                      onChange={formik.handleChange}
                      error={
                        formik.touched.pricingAnalysis &&
                        Boolean(formik.errors.pricingAnalysis)
                      }
                      helperText={
                        formik.touched.pricingAnalysis &&
                        formik.errors.pricingAnalysis
                      }
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 2,
                  }}
                >
                  <Typography variant="h6">Objections & Responses</Typography>
                  <Button startIcon={<AddIcon />} onClick={handleObjectionAdd}>
                    Add Objection
                  </Button>
                </Box>
                {formik.values.objections.map((obj, index) => (
                  <Box key={index} sx={{ mb: 3 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Objection"
                          value={obj.objection}
                          onChange={(e) => {
                            const newObjections = [...formik.values.objections];
                            newObjections[index].objection = e.target.value;
                            formik.setFieldValue('objections', newObjections);
                          }}
                          error={
                            formik.touched.objections &&
                            Boolean(formik.errors.objections)
                          }
                          helperText={
                            formik.touched.objections && formik.errors.objections
                          }
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex' }}>
                          <TextField
                            fullWidth
                            label="Response"
                            multiline
                            rows={2}
                            value={obj.response}
                            onChange={(e) => {
                              const newObjections = [...formik.values.objections];
                              newObjections[index].response = e.target.value;
                              formik.setFieldValue('objections', newObjections);
                            }}
                          />
                          <IconButton
                            onClick={() => handleObjectionRemove(index)}
                            disabled={formik.values.objections.length === 1}
                            sx={{ ml: 1 }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Grid>
                    </Grid>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Winning Strategies
                </Typography>
                {formik.values.winningStrategies.map((strategy, index) => (
                  <Box key={index} sx={{ display: 'flex', mb: 2 }}>
                    <TextField
                      fullWidth
                      label={`Strategy ${index + 1}`}
                      value={strategy}
                      onChange={(e) => {
                        const newStrategies = [...formik.values.winningStrategies];
                        newStrategies[index] = e.target.value;
                        formik.setFieldValue('winningStrategies', newStrategies);
                      }}
                      error={
                        formik.touched.winningStrategies &&
                        Boolean(formik.errors.winningStrategies)
                      }
                      helperText={
                        formik.touched.winningStrategies &&
                        formik.errors.winningStrategies
                      }
                    />
                    <IconButton
                      onClick={() =>
                        handleArrayFieldRemove('winningStrategies', index)
                      }
                      disabled={formik.values.winningStrategies.length === 1}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                ))}
                <Button
                  startIcon={<AddIcon />}
                  onClick={() => handleArrayFieldAdd('winningStrategies')}
                >
                  Add Strategy
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </form>

      <AIGenerationDialog
        open={aiDialogOpen}
        onClose={() => setAiDialogOpen(false)}
        onGenerate={handleAIGenerate}
        loading={aiLoading}
      />
    </Box>
  );
};

export default BattlecardEditor; 
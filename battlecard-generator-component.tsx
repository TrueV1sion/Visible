import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  CircularProgress, 
  Container, 
  Divider, 
  FormControl, 
  Grid, 
  IconButton, 
  InputLabel, 
  LinearProgress, 
  MenuItem, 
  Paper, 
  Select, 
  Stepper, 
  Step, 
  StepLabel, 
  Tab, 
  Tabs, 
  TextField, 
  Typography, 
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';

import {
  AddCircleOutline as AddIcon,
  AutoAwesome as AIIcon,
  DeleteOutline as DeleteIcon,
  EditOutlined as EditIcon,
  ExpandMore as ExpandMoreIcon,
  RefreshOutlined as RefreshIcon,
  SaveOutlined as SaveIcon,
  ContentCopy as CopyIcon,
  Download as DownloadIcon
} from 'lucide-react';

// Mock data for competitors
const COMPETITORS = [
  { id: 'comp1', name: 'Competitor A' },
  { id: 'comp2', name: 'Competitor B' },
  { id: 'comp3', name: 'Competitor C' },
  { id: 'comp4', name: 'Add Custom...' }
];

// Mock data for product segments
const PRODUCT_SEGMENTS = [
  { id: 'segment1', name: 'Enterprise' },
  { id: 'segment2', name: 'Mid-Market' },
  { id: 'segment3', name: 'Small Business' }
];

// Mock API call to generate battlecard
const generateBattlecard = async (data) => {
  console.log('Generating battlecard with data:', data);
  // In a real app, this would be an API call
  await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API delay
  
  // Return mock data
  return {
    status: 'success',
    data: {
      metadata: {
        generated_at: new Date().toISOString(),
        competitor: data.competitor_info.name
      },
      overview: {
        company_name: data.competitor_info.name,
        description: `${data.competitor_info.name} is a leading provider of ${data.competitor_info.primary_offering} solutions focusing on ${data.competitor_info.target_market} organizations.`,
        key_metrics: {
          founded: '2015',
          employees: '500+',
          funding: '$120M Series C (2023)'
        },
        target_market: ['Enterprise customers', 'Mid-market organizations', 'Healthcare sector'],
        recent_developments: [
          'Launched new AI-powered analytics platform',
          'Expanded operations to European market',
          'Acquired data visualization startup'
        ]
      },
      strengths_weaknesses: {
        strengths: [
          'Strong brand recognition',
          'Extensive enterprise customer base',
          'Robust feature set',
          'Well-established partner ecosystem'
        ],
        weaknesses: [
          'Higher pricing',
          'Complex implementation process',
          'Limited customization options',
          'Slower release cycle'
        ],
        opportunities: [
          'Gaps in customer support',
          'Missing key integrations',
          'Slow to adopt AI/ML capabilities'
        ],
        threats: [
          'Rapidly gaining market share',
          'Strong executive relationships',
          'Aggressive pricing strategies'
        ]
      },
      objection_handling: {
        objections: [
          {
            objection: `${data.competitor_info.name} is cheaper than your solution`,
            response: 'While their initial price point may appear lower, our total cost of ownership is typically 20% less over a three-year period due to our all-inclusive pricing model that avoids hidden fees and surcharges.',
            evidence: ['ROI calculator showing 3-year TCO', 'Case study: Company X saved $430K']
          },
          {
            objection: `${data.competitor_info.name} has more features than your product`,
            response: 'Our platform focuses on delivering the core features that drive 95% of customer value with superior quality and performance, rather than including rarely-used capabilities that add complexity and performance overhead.',
            evidence: ['Feature utilization analysis', 'Customer survey results']
          },
          {
            objection: `${data.competitor_info.name} has better market reputation/reviews`,
            response: 'While they do have strong brand recognition, if you look at recent reviews from the past 12 months, our customer satisfaction scores have overtaken theirs by 15 points, particularly in areas of support responsiveness and feature quality.',
            evidence: ['G2 Crowd comparison', 'Gartner Peer Insights trends']
          }
        ]
      },
      winning_strategies: {
        strategies: [
          {
            focus_area: 'Sales Cycle Positioning',
            strategy: 'Emphasize implementation speed and time-to-value',
            details: [
              'Highlight our 30-day implementation guarantee vs. their typical 90-day process',
              'Share case studies showing immediate ROI post-implementation',
              'Offer proof-of-concept in target environment'
            ],
            priority: 'High'
          },
          {
            focus_area: 'Technical Evaluation',
            strategy: 'Focus on user experience and simplicity',
            details: [
              'Push for hands-on evaluation by end users, not just technical team',
              'Demonstrate self-service capabilities not available in their platform',
              'Showcase our training completion rates (95%) vs. industry average (62%)'
            ],
            priority: 'Medium'
          },
          {
            focus_area: 'Pricing Discussions',
            strategy: 'Reframe value conversation to ROI not license cost',
            details: [
              'Present TCO calculator showing 3-year advantage',
              'Emphasize all-inclusive pricing vs. their module-based approach',
              'Demonstrate productivity gains that offset price difference'
            ],
            priority: 'High'
          }
        ]
      }
    }
  };
};

// Tab Panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`battlecard-tabpanel-${index}`}
      aria-labelledby={`battlecard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const BattlecardGenerator = () => {
  // State for wizard steps
  const [activeStep, setActiveStep] = useState(0);
  const steps = ['Select Competitor', 'Product Details', 'Generate & Review'];
  
  // State for form data
  const [formData, setFormData] = useState({
    competitor_info: {
      id: '',
      name: '',
      primary_offering: '',
      target_market: '',
      custom: false
    },
    product_segment: '',
    focus_areas: []
  });
  
  // State for custom competitor
  const [isCustomCompetitor, setIsCustomCompetitor] = useState(false);
  
  // State for focus areas
  const [focusAreas, setFocusAreas] = useState([
    { id: 'area1', value: 'Pricing comparison' },
    { id: 'area2', value: 'Feature differentiation' }
  ]);
  
  // State for generation process
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [battlecard, setBattlecard] = useState(null);
  
  // State for review tabs
  const [reviewTabValue, setReviewTabValue] = useState(0);
  
  // State for section editing
  const [editingSectionId, setEditingSectionId] = useState(null);
  const [editedSectionContent, setEditedSectionContent] = useState('');
  
  // Handle competitor selection
  const handleCompetitorChange = (event) => {
    const selectedId = event.target.value;
    const selected = COMPETITORS.find(comp => comp.id === selectedId);
    
    if (selected.id === 'comp4') {
      // Custom competitor selected
      setIsCustomCompetitor(true);
      setFormData({
        ...formData,
        competitor_info: {
          id: '',
          name: '',
          primary_offering: '',
          target_market: '',
          custom: true
        }
      });
    } else {
      setIsCustomCompetitor(false);
      setFormData({
        ...formData,
        competitor_info: {
          id: selected.id,
          name: selected.name,
          primary_offering: '',
          target_market: '',
          custom: false
        }
      });
    }
  };
  
  // Handle product segment selection
  const handleSegmentChange = (event) => {
    setFormData({
      ...formData,
      product_segment: event.target.value
    });
  };
  
  // Handle form field changes
  const handleInputChange = (field, value) => {
    setFormData(prev => {
      if (field.startsWith('competitor_info.')) {
        const subField = field.split('.')[1];
        return {
          ...prev,
          competitor_info: {
            ...prev.competitor_info,
            [subField]: value
          }
        };
      } else {
        return {
          ...prev,
          [field]: value
        };
      }
    });
  };
  
  // Add a new focus area
  const addFocusArea = () => {
    const newId = `area${focusAreas.length + 1}`;
    setFocusAreas([...focusAreas, { id: newId, value: '' }]);
  };
  
  // Update a focus area
  const updateFocusArea = (id, value) => {
    setFocusAreas(prev => 
      prev.map(area => area.id === id ? { ...area, value } : area)
    );
  };
  
  // Remove a focus area
  const removeFocusArea = (id) => {
    setFocusAreas(prev => prev.filter(area => area.id !== id));
  };
  
  // Navigate to next step
  const handleNext = () => {
    if (activeStep === 0) {
      // Validate competitor info
      if (!isCustomCompetitor && !formData.competitor_info.id) {
        alert('Please select a competitor');
        return;
      }
      if (isCustomCompetitor && !formData.competitor_info.name) {
        alert('Please enter competitor name');
        return;
      }
    } else if (activeStep === 1) {
      // Validate product details
      if (!formData.product_segment) {
        alert('Please select a product segment');
        return;
      }
      
      // Collect focus areas
      const validFocusAreas = focusAreas.filter(area => area.value.trim() !== '');
      setFormData(prev => ({
        ...prev,
        focus_areas: validFocusAreas.map(area => area.value)
      }));
    }
    
    setActiveStep((prevStep) => prevStep + 1);
  };
  
  // Navigate to previous step
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };
  
  // Generate the battlecard
  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenerationProgress(0);
    
    // Simulate progressive generation progress
    const progressInterval = setInterval(() => {
      setGenerationProgress(prev => {
        const newProgress = prev + Math.random() * 15;
        return newProgress >= 100 ? 100 : newProgress;
      });
    }, 500);
    
    try {
      // Call generation API
      const result = await generateBattlecard(formData);
      
      if (result.status === 'success') {
        setBattlecard(result.data);
        setReviewTabValue(0); // Reset to first tab
      } else {
        alert('Error generating battlecard: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Generation error:', error);
      alert('An error occurred during generation. Please try again.');
    } finally {
      clearInterval(progressInterval);
      setGenerationProgress(100);
      setTimeout(() => {
        setIsGenerating(false);
      }, 500);
    }
  };
  
  // Handle tab change in review panel
  const handleTabChange = (event, newValue) => {
    setReviewTabValue(newValue);
  };
  
  // Start editing a section
  const handleEditSection = (sectionId, content) => {
    setEditingSectionId(sectionId);
    setEditedSectionContent(content);
  };
  
  // Save edited section
  const handleSaveSection = (sectionId) => {
    // In a real app, this would call an API to update the content
    setBattlecard(prev => {
      const updated = { ...prev };
      
      if (sectionId === 'overview.description') {
        updated.overview.description = editedSectionContent;
      } else if (sectionId.startsWith('strengths_weaknesses')) {
        const [section, index] = sectionId.split('.')[1].split('-');
        updated.strengths_weaknesses[section][parseInt(index)] = editedSectionContent;
      } else if (sectionId.startsWith('objection_handling')) {
        const [field, index] = sectionId.split('.')[1].split('-');
        const objIdx = parseInt(index);
        updated.objection_handling.objections[objIdx][field] = editedSectionContent;
      } else if (sectionId.startsWith('winning_strategies')) {
        const [field, index1, index2] = sectionId.split('.')[1].split('-');
        const stratIdx = parseInt(index1);
        
        if (field === 'strategy') {
          updated.winning_strategies.strategies[stratIdx].strategy = editedSectionContent;
        } else if (field === 'detail') {
          updated.winning_strategies.strategies[stratIdx].details[parseInt(index2)] = editedSectionContent;
        }
      }
      
      return updated;
    });
    
    setEditingSectionId(null);
    setEditedSectionContent('');
  };
  
  // Cancel editing
  const handleCancelEdit = () => {
    setEditingSectionId(null);
    setEditedSectionContent('');
  };
  
  // Regenerate a specific section
  const handleRegenerateSection = async (sectionId) => {
    // In a real app, this would call an API to regenerate just this section
    alert(`Regenerating section: ${sectionId}`);
  };
  
  // Copy battlecard to clipboard
  const handleCopyBattlecard = () => {
    const text = JSON.stringify(battlecard, null, 2);
    navigator.clipboard.writeText(text).then(
      () => alert('Battlecard copied to clipboard!'),
      (err) => console.error('Could not copy text: ', err)
    );
  };
  
  // Download battlecard as JSON
  const handleDownloadBattlecard = () => {
    const dataStr = JSON.stringify(battlecard, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileName = `battlecard-${formData.competitor_info.name.replace(/\s+/g, '-').toLowerCase()}-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileName);
    linkElement.click();
  };
  
  // Render competitor selection step
  const renderCompetitorStep = () => {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Select Competitor
        </Typography>
        
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="competitor-select-label">Competitor</InputLabel>
          <Select
            labelId="competitor-select-label"
            value={isCustomCompetitor ? 'comp4' : formData.competitor_info.id}
            label="Competitor"
            onChange={handleCompetitorChange}
          >
            {COMPETITORS.map(competitor => (
              <MenuItem key={competitor.id} value={competitor.id}>
                {competitor.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        {isCustomCompetitor && (
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              label="Competitor Name"
              value={formData.competitor_info.name}
              onChange={(e) => handleInputChange('competitor_info.name', e.target.value)}
              sx={{ mb: 2 }}
            />
          </Box>
        )}
        
        <TextField
          fullWidth
          label="Primary Offering"
          value={formData.competitor_info.primary_offering}
          onChange={(e) => handleInputChange('competitor_info.primary_offering', e.target.value)}
          placeholder="e.g. Cloud Security, CRM, Marketing Automation"
          sx={{ mb: 2 }}
        />
        
        <TextField
          fullWidth
          label="Target Market"
          value={formData.competitor_info.target_market}
          onChange={(e) => handleInputChange('competitor_info.target_market', e.target.value)}
          placeholder="e.g. Enterprise, SMB, Healthcare"
          sx={{ mb: 2 }}
        />
      </Box>
    );
  };
  
  // Render product details step
  const renderProductStep = () => {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Product Details
        </Typography>
        
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="segment-select-label">Product Segment</InputLabel>
          <Select
            labelId="segment-select-label"
            value={formData.product_segment}
            label="Product Segment"
            onChange={handleSegmentChange}
          >
            {PRODUCT_SEGMENTS.map(segment => (
              <MenuItem key={segment.id} value={segment.id}>
                {segment.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Typography variant="subtitle1" gutterBottom>
          Focus Areas
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Specify areas to highlight in the battlecard
        </Typography>
        
        {focusAreas.map((area, index) => (
          <Box 
            key={area.id} 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              mb: 2 
            }}
          >
            <TextField
              fullWidth
              label={`Focus Area ${index + 1}`}
              value={area.value}
              onChange={(e) => updateFocusArea(area.id, e.target.value)}
              placeholder="e.g. Pricing, Security Features, Integrations"
            />
            <IconButton 
              color="error" 
              onClick={() => removeFocusArea(area.id)}
              disabled={focusAreas.length <= 1}
              sx={{ ml: 1 }}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        ))}
        
        <Button
          startIcon={<AddIcon />}
          onClick={addFocusArea}
          sx={{ mt: 1 }}
        >
          Add Focus Area
        </Button>
      </Box>
    );
  };
  
  // Render generation and review step
  const renderGenerateStep = () => {
    if (isGenerating || !battlecard) {
      return (
        <Box sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom align="center">
            Generating Battlecard
          </Typography>
          
          <Box sx={{ width: '100%', mt: 4, mb: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={generationProgress} 
              sx={{ height: 10, borderRadius: 5 }}
            />
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
              {Math.round(generationProgress)}% Complete
            </Typography>
          </Box>
          
          {!battlecard && !isGenerating && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Button 
                variant="contained" 
                startIcon={<AIIcon />}
                onClick={handleGenerate}
              >
                Generate Battlecard
              </Button>
            </Box>
          )}
        </Box>
      );
    }
    
    return (
      <Box sx={{ p: 3 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            mb: 2
          }}
        >
          <Typography variant="h5">
            {battlecard.metadata.competitor} Battlecard
          </Typography>
          
          <Box>
            <IconButton onClick={handleCopyBattlecard} title="Copy to clipboard">
              <CopyIcon />
            </IconButton>
            <IconButton onClick={handleDownloadBattlecard} title="Download as JSON">
              <DownloadIcon />
            </IconButton>
          </Box>
        </Box>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={reviewTabValue} 
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="Overview" />
            <Tab label="Strengths & Weaknesses" />
            <Tab label="Objection Handling" />
            <Tab label="Winning Strategies" />
          </Tabs>
        </Box>
        
        <TabPanel value={reviewTabValue} index={0}>
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'flex-start',
                  mb: 2
                }}
              >
                <Typography variant="h6">Company Overview</Typography>
                <Box>
                  {editingSectionId === 'overview.description' ? (
                    <>
                      <IconButton size="small" onClick={() => handleSaveSection('overview.description')}>
                        <SaveIcon />
                      </IconButton>
                      <IconButton size="small" onClick={handleCancelEdit}>
                        <DeleteIcon />
                      </IconButton>
                    </>
                  ) : (
                    <>
                      <IconButton 
                        size="small" 
                        onClick={() => handleEditSection('overview.description', battlecard.overview.description)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        onClick={() => handleRegenerateSection('overview')}
                      >
                        <RefreshIcon />
                      </IconButton>
                    </>
                  )}
                </Box>
              </Box>
              
              {editingSectionId === 'overview.description' ? (
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  value={editedSectionContent}
                  onChange={(e) => setEditedSectionContent(e.target.value)}
                  sx={{ mb: 2 }}
                />
              ) : (
                <Typography variant="body1" paragraph>
                  {battlecard.overview.description}
                </Typography>
              )}
              
              <Typography variant="subtitle1">Target Market</Typography>
              <Box sx={{ mb: 2 }}>
                {battlecard.overview.target_market.map((market, idx) => (
                  <Chip key={idx} label={market} sx={{ mr: 1, mb: 1 }} />
                ))}
              </Box>
              
              <Typography variant="subtitle1">Recent Developments</Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                {battlecard.overview.recent_developments.map((development, idx) => (
                  <li key={idx}>
                    <Typography variant="body2">
                      {development}
                    </Typography>
                  </li>
                ))}
              </Box>
            </CardContent>
          </Card>
        </TabPanel>
        
        <TabPanel value={reviewTabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'flex-start',
                      mb: 2
                    }}
                  >
                    <Typography variant="h6">Strengths</Typography>
                    <IconButton 
                      size="small" 
                      onClick={() => handleRegenerateSection('strengths_weaknesses.strengths')}
                    >
                      <RefreshIcon />
                    </IconButton>
                  </Box>
                  
                  <Box component="ul" sx={{ pl: 2 }}>
                    {battlecard.strengths_weaknesses.strengths.map((strength, idx) => (
                      <li key={idx}>
                        {editingSectionId === `strengths_weaknesses.strengths-${idx}` ? (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <TextField
                              fullWidth
                              value={editedSectionContent}
                              onChange={(e) => setEditedSectionContent(e.target.value)}
                              size="small"
                            />
                            <IconButton 
                              size="small" 
                              onClick={() => handleSaveSection(`strengths_weaknesses.strengths-${idx}`)}
                            >
                              <SaveIcon />
                            </IconButton>
                            <IconButton size="small" onClick={handleCancelEdit}>
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        ) : (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body1" sx={{ flex: 1 }}>
                              {strength}
                            </Typography>
                            <IconButton 
                              size="small" 
                              onClick={() => handleEditSection(`strengths_weaknesses.strengths-${idx}`, strength)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Box>
                        )}
                      </li>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent>
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'flex-start',
                      mb: 2
                    }}
                  >
                    <Typography variant="h6">Weaknesses</Typography>
                    <IconButton 
                      size="small" 
                      onClick={() => handleRegenerateSection('strengths_weaknesses.weaknesses')}
                    >
                      <RefreshIcon />
                    </IconButton>
                  </Box>
                  
                  <Box component="ul" sx={{ pl: 2 }}>
                    {battlecard.strengths_weaknesses.weaknesses.map((weakness, idx) => (
                      <li key={idx}>
                        {editingSectionId === `strengths_weaknesses.weaknesses-${idx}` ? (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <TextField
                              fullWidth
                              value={editedSectionContent}
                              onChange={(e) => setEditedSectionContent(e.target.value)}
                              size="small"
                            />
                            <IconButton 
                              size="small" 
                              onClick={() => handleSaveSection(`strengths_weaknesses.weaknesses-${idx}`)}
                            >
                              <SaveIcon />
                            </IconButton>
                            <IconButton size="small" onClick={handleCancelEdit}>
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        ) : (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body1" sx={{ flex: 1 }}>
                              {weakness}
                            </Typography>
                            <IconButton 
                              size="small" 
                              onClick={() => handleEditSection(`strengths_weaknesses.weaknesses-${idx}`, weakness)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Box>
                        )}
                      </li>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
        
        <TabPanel value={reviewTabValue} index={2}>
          {battlecard.objection_handling.objections.map((objection, idx) => (
            <Accordion key={idx} defaultExpanded={idx === 0}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight="medium">
                  {objection.objection}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'flex-start',
                      mb: 1
                    }}
                  >
                    <Typography variant="subtitle1">Response</Typography>
                    <Box>
                      {editingSectionId === `objection_handling.response-${idx}` ? (
                        <>
                          <IconButton 
                            size="small" 
                            onClick={() => handleSaveSection(`objection_handling.response-${idx}`)}
                          >
                            <SaveIcon />
                          </IconButton>
                          <IconButton size="small" onClick={handleCancelEdit}>
                            <DeleteIcon />
                          </IconButton>
                        </>
                      ) : (
                        <>
                          <IconButton 
                            size="small" 
                            onClick={() => handleEditSection(`objection_handling.response-${idx}`, objection.response)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            onClick={() => handleRegenerateSection(`objection_handling.response-${idx}`)}
                          >
                            <RefreshIcon />
                          </IconButton>
                        </>
                      )}
                    </Box>
                  </Box>
                  
                  {editingSectionId === `objection_handling.response-${idx}` ? (
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      value={editedSectionContent}
                      onChange={(e) => setEditedSectionContent(e.target.value)}
                      sx={{ mb: 2 }}
                    />
                  ) : (
                    <Typography variant="body1" paragraph>
                      {objection.response}
                    </Typography>
                  )}
                  
                  {objection.evidence.length > 0 && (
                    <>
                      <Typography variant="subtitle1">Supporting Evidence</Typography>
                      <Box component="ul" sx={{ pl: 2 }}>
                        {objection.evidence.map((item, evidenceIdx) => (
                          <li key={evidenceIdx}>
                            <Typography variant="body2">
                              {item}
                            </Typography>
                          </li>
                        ))}
                      </Box>
                    </>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </TabPanel>
        
        <TabPanel value={reviewTabValue} index={3}>
          {battlecard.winning_strategies.strategies.map((strategy, idx) => (
            <Card key={idx} variant="outlined" sx={{ mb: 3 }}>
              <CardContent>
                <Box 
                  sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'flex-start',
                    mb: 2
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h6">{strategy.focus_area}</Typography>
                    <Chip 
                      label={strategy.priority} 
                      color={strategy.priority === 'High' ? 'error' : 'warning'} 
                      size="small" 
                    />
                  </Box>
                  <IconButton 
                    size="small" 
                    onClick={() => handleRegenerateSection(`winning_strategies-${idx}`)}
                  >
                    <RefreshIcon />
                  </IconButton>
                </Box>
                
                {editingSectionId === `winning_strategies.strategy-${idx}` ? (
                  <Box sx={{ mb: 2 }}>
                    <TextField
                      fullWidth
                      value={editedSectionContent}
                      onChange={(e) => setEditedSectionContent(e.target.value)}
                      size="small"
                      sx={{ mb: 1 }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <IconButton 
                        size="small" 
                        onClick={() => handleSaveSection(`winning_strategies.strategy-${idx}`)}
                      >
                        <SaveIcon />
                      </IconButton>
                      <IconButton size="small" onClick={handleCancelEdit}>
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>
                ) : (
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      mb: 2 
                    }}
                  >
                    <Typography variant="subtitle1" sx={{ flex: 1 }}>
                      {strategy.strategy}
                    </Typography>
                    <IconButton 
                      size="small" 
                      onClick={() => handleEditSection(`winning_strategies.strategy-${idx}`, strategy.strategy)}
                    >
                      <EditIcon />
                    </IconButton>
                  </Box>
                )}
                
                <Box component="ul" sx={{ pl: 2 }}>
                  {strategy.details.map((detail, detailIdx) => (
                    <li key={detailIdx}>
                      {editingSectionId === `winning_strategies.detail-${idx}-${detailIdx}` ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <TextField
                            fullWidth
                            value={editedSectionContent}
                            onChange={(e) => setEditedSectionContent(e.target.value)}
                            size="small"
                          />
                          <IconButton 
                            size="small" 
                            onClick={() => handleSaveSection(`winning_strategies.detail-${idx}-${detailIdx}`)}
                          >
                            <SaveIcon />
                          </IconButton>
                          <IconButton size="small" onClick={handleCancelEdit}>
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      ) : (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body1" sx={{ flex: 1 }}>
                            {detail}
                          </Typography>
                          <IconButton 
                            size="small" 
                            onClick={() => handleEditSection(`winning_strategies.detail-${idx}-${detailIdx}`, detail)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Box>
                      )}
                    </li>
                  ))}
                </Box>
              </CardContent>
            </Card>
          ))}
        </TabPanel>
      </Box>
    );
  };
  
  // Render current step content
  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return renderCompetitorStep();
      case 1:
        return renderProductStep();
      case 2:
        return renderGenerateStep();
      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ mt: 3, mb: 6 }}>
        <Box sx={{ p: 2, borderBottom: '1px solid #eee' }}>
          <Typography variant="h5" align="center">
            AI Battlecard Generator
          </Typography>
        </Box>
        
        <Stepper activeStep={activeStep} sx={{ p: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Box>
          {renderStepContent(activeStep)}
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', p: 3, borderTop: '1px solid #eee' }}>
            <Button
              variant="outlined"
              onClick={handleBack}
              disabled={activeStep === 0 || (activeStep === 2 && isGenerating)}
            >
              Back
            </Button>
            
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleGenerate}
                startIcon={<AIIcon />}
                disabled={isGenerating || (battlecard !== null)}
              >
                {battlecard ? 'Generated' : 'Generate Battlecard'}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Container>
  );
  
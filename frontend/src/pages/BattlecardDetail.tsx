import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  IconButton,
  Paper,
  Typography,
  Tab,
  Tabs,
} from '@mui/material';
import {
  Edit as EditIcon,
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`battlecard-tabpanel-${index}`}
    aria-labelledby={`battlecard-tab-${index}`}
  >
    {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
  </div>
);

interface Battlecard {
  id: string;
  title: string;
  competitor: string;
  lastUpdated: string;
  status: 'draft' | 'published' | 'archived';
  overview: string;
  strengthsWeaknesses: {
    strengths: string[];
    weaknesses: string[];
  };
  competitiveAdvantages: string[];
  pricingComparison: {
    ourPricing: string;
    theirPricing: string;
    analysis: string;
  };
  commonObjections: Array<{
    objection: string;
    response: string;
  }>;
  winningStrategies: string[];
  tags: string[];
}

const BattlecardDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = React.useState(0);

  // Mock data - replace with API call
  const battlecard: Battlecard = {
    id: '1',
    title: 'Competitor X Enterprise Solution',
    competitor: 'Competitor X',
    lastUpdated: '2024-03-15',
    status: 'published',
    overview:
      'Competitor X is a leading provider of enterprise solutions focusing on large organizations...',
    strengthsWeaknesses: {
      strengths: [
        'Strong brand recognition',
        'Extensive enterprise customer base',
        'Robust feature set',
      ],
      weaknesses: [
        'Higher pricing',
        'Complex implementation process',
        'Limited customization options',
      ],
    },
    competitiveAdvantages: [
      'More flexible pricing model',
      'Faster implementation time',
      'Better customer support',
      'More extensive integration options',
    ],
    pricingComparison: {
      ourPricing: 'Starting at $499/month',
      theirPricing: 'Starting at $999/month',
      analysis:
        'Our pricing provides better value with more included features and no hidden costs...',
    },
    commonObjections: [
      {
        objection: 'They have more features',
        response:
          'While they may have more features, our solution focuses on the most important ones...',
      },
      {
        objection: 'They have better market presence',
        response:
          'Our focused approach allows us to provide better specialized solutions...',
      },
    ],
    winningStrategies: [
      'Focus on implementation speed',
      'Emphasize cost-effectiveness',
      'Highlight superior customer support',
    ],
    tags: ['Enterprise', 'Cloud', 'Security'],
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

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
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/battlecards')}
        >
          Back to Battlecards
        </Button>
        <Box>
          <IconButton onClick={() => console.log('Download')}>
            <DownloadIcon />
          </IconButton>
          <IconButton onClick={() => console.log('Share')}>
            <ShareIcon />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<EditIcon />}
            onClick={() => navigate(`/battlecards/${id}/edit`)}
            sx={{ ml: 2 }}
          >
            Edit
          </Button>
        </Box>
      </Box>

      <Paper elevation={2} sx={{ mb: 3, p: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h4" gutterBottom>
              {battlecard.title}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              {battlecard.competitor}
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Chip
                label={battlecard.status}
                color={getStatusColor(battlecard.status)}
                sx={{ mr: 1 }}
              />
              {battlecard.tags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  variant="outlined"
                  sx={{ mr: 1 }}
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Overview" />
          <Tab label="Strengths & Weaknesses" />
          <Tab label="Competitive Advantages" />
          <Tab label="Pricing" />
          <Tab label="Objection Handling" />
          <Tab label="Winning Strategies" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Typography variant="body1">{battlecard.overview}</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Strengths
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  {battlecard.strengthsWeaknesses.strengths.map((strength) => (
                    <Typography component="li" key={strength}>
                      {strength}
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Weaknesses
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  {battlecard.strengthsWeaknesses.weaknesses.map((weakness) => (
                    <Typography component="li" key={weakness}>
                      {weakness}
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Box component="ul" sx={{ pl: 2 }}>
          {battlecard.competitiveAdvantages.map((advantage) => (
            <Typography component="li" key={advantage}>
              {advantage}
            </Typography>
          ))}
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Our Pricing
                </Typography>
                <Typography>{battlecard.pricingComparison.ourPricing}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Their Pricing
                </Typography>
                <Typography>
                  {battlecard.pricingComparison.theirPricing}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Pricing Analysis
                </Typography>
                <Typography>{battlecard.pricingComparison.analysis}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        {battlecard.commonObjections.map((item, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {item.objection}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography>{item.response}</Typography>
            </CardContent>
          </Card>
        ))}
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        <Box component="ul" sx={{ pl: 2 }}>
          {battlecard.winningStrategies.map((strategy) => (
            <Typography component="li" key={strategy}>
              {strategy}
            </Typography>
          ))}
        </Box>
      </TabPanel>
    </Box>
  );
};

export default BattlecardDetail; 
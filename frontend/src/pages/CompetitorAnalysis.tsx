import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import { AutoAwesome as AutoAwesomeIcon } from '@mui/icons-material';
import axios from 'axios';

interface CompetitorAnalysisResult {
  overview: string;
  marketPosition: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  recommendations: string[];
}

const CompetitorAnalysis: React.FC = () => {
  const [competitor, setCompetitor] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CompetitorAnalysisResult | null>(null);

  const handleAnalyze = async () => {
    if (!competitor.trim()) {
      setError('Please enter a competitor name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/v1/ai/competitive-analysis', {
        input_data: {
          competitor_name: competitor,
          data_points: [
            // Example data points
            'Recent product launch',
            'Price change Q1',
            'Acquisition rumor'
          ],
          historical_data: [
            // If you have historical context
          ]
        }
      });

      if (response && response.data) {
        setResult(response.data);
      }
    } catch (err) {
      setError('Failed to analyze competitor. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Competitor Analysis
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Competitor Name"
                value={competitor}
                onChange={(e) => setCompetitor(e.target.value)}
                placeholder="Enter competitor name to analyze"
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleAnalyze}
                disabled={loading}
                startIcon={
                  loading ? <CircularProgress size={20} /> : <AutoAwesomeIcon />
                }
              >
                {loading ? 'Analyzing...' : 'Analyze Competitor'}
              </Button>
            </Grid>
          </Grid>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {result && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Overview
                </Typography>
                <Typography variant="body1">{result.overview}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Position
                </Typography>
                <Typography variant="body1">{result.marketPosition}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Strengths
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  {result.strengths.map((strength, index) => (
                    <Typography component="li" key={index}>
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
                  {result.weaknesses.map((weakness, index) => (
                    <Typography component="li" key={index}>
                      {weakness}
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
                  Opportunities
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  {result.opportunities.map((opportunity, index) => (
                    <Typography component="li" key={index}>
                      {opportunity}
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
                  Threats
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  {result.threats.map((threat, index) => (
                    <Typography component="li" key={index}>
                      {threat}
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recommendations
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  {result.recommendations.map((recommendation, index) => (
                    <Typography component="li" key={index}>
                      {recommendation}
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default CompetitorAnalysis; 
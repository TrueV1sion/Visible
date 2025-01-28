import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CompetitorAnalysis from '../CompetitorAnalysis';

// Mock result data
const mockAnalysisResult = {
  overview: 'Competitor X is a well-established player in the market...',
  marketPosition: 'Currently holds approximately 15% market share...',
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
  opportunities: [
    'Expanding into mid-market segment',
    'Cloud migration services',
    'AI/ML integration',
  ],
  threats: [
    'Increasing competition in core market',
    'Rapid technological changes',
    'Price pressure from new entrants',
  ],
  recommendations: [
    'Focus on differentiation through superior customer support',
    'Emphasize faster implementation times',
    'Highlight cost-effectiveness and ROI',
  ],
};

// Wrapper component for providing router context
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('CompetitorAnalysis Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the component with title', () => {
    render(<CompetitorAnalysis />, { wrapper });
    expect(screen.getByText('Competitor Analysis')).toBeInTheDocument();
  });

  it('displays input field and analyze button', () => {
    render(<CompetitorAnalysis />, { wrapper });
    expect(screen.getByLabelText('Competitor Name')).toBeInTheDocument();
    expect(screen.getByText('Analyze Competitor')).toBeInTheDocument();
  });

  it('shows error when analyzing without competitor name', () => {
    render(<CompetitorAnalysis />, { wrapper });
    fireEvent.click(screen.getByText('Analyze Competitor'));
    expect(screen.getByText('Please enter a competitor name')).toBeInTheDocument();
  });

  it('shows loading state during analysis', async () => {
    render(<CompetitorAnalysis />, { wrapper });
    
    // Enter competitor name
    const input = screen.getByLabelText('Competitor Name');
    fireEvent.change(input, { target: { value: 'Competitor X' } });
    
    // Click analyze button
    fireEvent.click(screen.getByText('Analyze Competitor'));
    
    // Verify loading state
    expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Wait for analysis to complete
    await waitFor(() => {
      expect(screen.queryByText('Analyzing...')).not.toBeInTheDocument();
    });
  });

  it('displays analysis results after successful analysis', async () => {
    render(<CompetitorAnalysis />, { wrapper });
    
    // Enter competitor name and trigger analysis
    const input = screen.getByLabelText('Competitor Name');
    fireEvent.change(input, { target: { value: 'Competitor X' } });
    fireEvent.click(screen.getByText('Analyze Competitor'));
    
    // Wait for and verify results
    await waitFor(() => {
      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Market Position')).toBeInTheDocument();
      expect(screen.getByText('Strengths')).toBeInTheDocument();
      expect(screen.getByText('Weaknesses')).toBeInTheDocument();
      expect(screen.getByText('Opportunities')).toBeInTheDocument();
      expect(screen.getByText('Threats')).toBeInTheDocument();
      expect(screen.getByText('Recommendations')).toBeInTheDocument();
    });

    // Verify specific content
    expect(screen.getByText(mockAnalysisResult.overview)).toBeInTheDocument();
    expect(screen.getByText(mockAnalysisResult.marketPosition)).toBeInTheDocument();
    
    // Verify lists
    mockAnalysisResult.strengths.forEach(strength => {
      expect(screen.getByText(strength)).toBeInTheDocument();
    });
    
    mockAnalysisResult.weaknesses.forEach(weakness => {
      expect(screen.getByText(weakness)).toBeInTheDocument();
    });
    
    mockAnalysisResult.opportunities.forEach(opportunity => {
      expect(screen.getByText(opportunity)).toBeInTheDocument();
    });
    
    mockAnalysisResult.threats.forEach(threat => {
      expect(screen.getByText(threat)).toBeInTheDocument();
    });
    
    mockAnalysisResult.recommendations.forEach(recommendation => {
      expect(screen.getByText(recommendation)).toBeInTheDocument();
    });
  });

  it('disables input and button during analysis', async () => {
    render(<CompetitorAnalysis />, { wrapper });
    
    // Enter competitor name
    const input = screen.getByLabelText('Competitor Name');
    fireEvent.change(input, { target: { value: 'Competitor X' } });
    
    // Click analyze button
    fireEvent.click(screen.getByText('Analyze Competitor'));
    
    // Verify disabled state
    expect(input).toBeDisabled();
    expect(screen.getByRole('button')).toBeDisabled();
    
    // Wait for analysis to complete
    await waitFor(() => {
      expect(input).not.toBeDisabled();
      expect(screen.getByRole('button')).not.toBeDisabled();
    });
  });

  it('clears error when starting new analysis', async () => {
    render(<CompetitorAnalysis />, { wrapper });
    
    // Trigger error
    fireEvent.click(screen.getByText('Analyze Competitor'));
    expect(screen.getByText('Please enter a competitor name')).toBeInTheDocument();
    
    // Start new analysis
    const input = screen.getByLabelText('Competitor Name');
    fireEvent.change(input, { target: { value: 'Competitor X' } });
    fireEvent.click(screen.getByText('Analyze Competitor'));
    
    // Verify error is cleared
    expect(screen.queryByText('Please enter a competitor name')).not.toBeInTheDocument();
  });
}); 
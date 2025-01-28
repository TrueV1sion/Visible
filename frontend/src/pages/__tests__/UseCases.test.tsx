import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import UseCases from '../UseCases';

// Mock data
const mockUseCase = {
  id: '1',
  title: 'Enterprise Customer Success Story',
  industry: 'Technology',
  challenge: 'A large enterprise customer needed to streamline their operations...',
  solution: 'We implemented our platform with custom integrations to address...',
  results: [
    '50% reduction in processing time',
    '30% cost savings',
    'Improved customer satisfaction',
  ],
  tags: ['Enterprise', 'Integration', 'Automation'],
};

// Wrapper component for providing router context
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('UseCases Component', () => {
  beforeEach(() => {
    // Reset any mocks before each test
    jest.clearAllMocks();
  });

  it('renders the component with title', () => {
    render(<UseCases />, { wrapper });
    expect(screen.getByText('Use Cases')).toBeInTheDocument();
  });

  it('displays search and filter controls', () => {
    render(<UseCases />, { wrapper });
    expect(screen.getByPlaceholderText('Search by title...')).toBeInTheDocument();
    expect(screen.getByText('Technology')).toBeInTheDocument();
    expect(screen.getByText('Healthcare')).toBeInTheDocument();
    expect(screen.getByText('Add New')).toBeInTheDocument();
  });

  it('displays initial use case', () => {
    render(<UseCases />, { wrapper });
    expect(screen.getByText(mockUseCase.title)).toBeInTheDocument();
    expect(screen.getByText(`Industry: ${mockUseCase.industry}`)).toBeInTheDocument();
  });

  it('opens dialog when Add New button is clicked', () => {
    render(<UseCases />, { wrapper });
    fireEvent.click(screen.getByText('Add New'));
    expect(screen.getByText('Add New Use Case')).toBeInTheDocument();
  });

  it('filters use cases by search query', () => {
    render(<UseCases />, { wrapper });
    const searchInput = screen.getByPlaceholderText('Search by title...');
    fireEvent.change(searchInput, { target: { value: 'Enterprise' } });
    expect(screen.getByText(mockUseCase.title)).toBeInTheDocument();
    
    fireEvent.change(searchInput, { target: { value: 'NonexistentCase' } });
    expect(screen.queryByText(mockUseCase.title)).not.toBeInTheDocument();
  });

  it('filters use cases by industry', () => {
    render(<UseCases />, { wrapper });
    fireEvent.click(screen.getByText('Healthcare'));
    expect(screen.queryByText(mockUseCase.title)).not.toBeInTheDocument();
    
    fireEvent.click(screen.getByText('Technology'));
    expect(screen.getByText(mockUseCase.title)).toBeInTheDocument();
  });

  it('adds a new use case', async () => {
    render(<UseCases />, { wrapper });
    
    // Open dialog
    fireEvent.click(screen.getByText('Add New'));
    
    // Fill form
    fireEvent.change(screen.getByLabelText('Title'), {
      target: { value: 'New Use Case' },
    });
    fireEvent.change(screen.getByLabelText('Industry'), {
      target: { value: 'Healthcare' },
    });
    fireEvent.change(screen.getByLabelText('Challenge'), {
      target: { value: 'Test challenge' },
    });
    fireEvent.change(screen.getByLabelText('Solution'), {
      target: { value: 'Test solution' },
    });
    
    // Add a result
    fireEvent.click(screen.getByText('Add Result'));
    const resultInput = screen.getByLabelText('Result 1');
    fireEvent.change(resultInput, { target: { value: 'Test result' } });
    
    // Add a tag
    const tagInput = screen.getByLabelText('Add tags (press Enter)');
    fireEvent.change(tagInput, { target: { value: 'TestTag' } });
    fireEvent.keyDown(tagInput, { key: 'Enter' });
    
    // Save
    fireEvent.click(screen.getByText('Save'));
    
    // Verify new use case is displayed
    await waitFor(() => {
      expect(screen.getByText('New Use Case')).toBeInTheDocument();
    });
  });

  it('edits an existing use case', async () => {
    render(<UseCases />, { wrapper });
    
    // Click edit button
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    fireEvent.click(editButtons[0]);
    
    // Modify title
    const titleInput = screen.getByLabelText('Title');
    fireEvent.change(titleInput, { target: { value: 'Updated Use Case' } });
    
    // Save
    fireEvent.click(screen.getByText('Save'));
    
    // Verify changes
    await waitFor(() => {
      expect(screen.getByText('Updated Use Case')).toBeInTheDocument();
    });
  });

  it('deletes a use case', () => {
    render(<UseCases />, { wrapper });
    
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    expect(screen.queryByText(mockUseCase.title)).not.toBeInTheDocument();
  });

  it('generates content using AI', async () => {
    render(<UseCases />, { wrapper });
    
    // Open dialog
    fireEvent.click(screen.getByText('Add New'));
    
    // Click generate button for challenge
    const generateButtons = screen.getAllByText('Generate');
    fireEvent.click(generateButtons[0]);
    
    // Verify loading state
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Verify generated content
    await waitFor(() => {
      expect(screen.getByLabelText('Challenge')).toHaveValue(
        expect.stringContaining('Based on our analysis')
      );
    });
  });

  it('validates required fields', async () => {
    render(<UseCases />, { wrapper });
    
    // Open dialog
    fireEvent.click(screen.getByText('Add New'));
    
    // Try to save without filling required fields
    fireEvent.click(screen.getByText('Save'));
    
    // Verify error message
    expect(screen.getByText('Please fill in all required fields')).toBeInTheDocument();
  });

  it('handles tag management', () => {
    render(<UseCases />, { wrapper });
    
    // Open dialog
    fireEvent.click(screen.getByText('Add New'));
    
    // Add tags
    const tagInput = screen.getByLabelText('Add tags (press Enter)');
    fireEvent.change(tagInput, { target: { value: 'Tag1' } });
    fireEvent.keyDown(tagInput, { key: 'Enter' });
    fireEvent.change(tagInput, { target: { value: 'Tag2' } });
    fireEvent.keyDown(tagInput, { key: 'Enter' });
    
    // Verify tags are added
    expect(screen.getByText('Tag1')).toBeInTheDocument();
    expect(screen.getByText('Tag2')).toBeInTheDocument();
    
    // Delete a tag
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    // Verify tag is removed
    expect(screen.queryByText('Tag1')).not.toBeInTheDocument();
    expect(screen.getByText('Tag2')).toBeInTheDocument();
  });
}); 
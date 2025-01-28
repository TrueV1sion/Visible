import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ObjectionLibrary from '../ObjectionLibrary';

// Mock data
const mockObjection = {
  id: '1',
  objection: 'Your product is too expensive',
  response: 'While our pricing may be higher initially, our solution provides superior ROI through...',
  category: 'Pricing',
  tags: ['Price', 'Value', 'ROI'],
};

// Wrapper component for providing router context
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('ObjectionLibrary Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the component with title', () => {
    render(<ObjectionLibrary />, { wrapper });
    expect(screen.getByText('Objection Library')).toBeInTheDocument();
  });

  it('displays search and filter controls', () => {
    render(<ObjectionLibrary />, { wrapper });
    expect(screen.getByPlaceholderText('Search by objection text...')).toBeInTheDocument();
    expect(screen.getByText('Pricing')).toBeInTheDocument();
    expect(screen.getByText('Competition')).toBeInTheDocument();
    expect(screen.getByText('Add New')).toBeInTheDocument();
  });

  it('displays initial objection', () => {
    render(<ObjectionLibrary />, { wrapper });
    expect(screen.getByText(mockObjection.objection)).toBeInTheDocument();
    expect(screen.getByText(mockObjection.response)).toBeInTheDocument();
  });

  it('opens dialog when Add New button is clicked', () => {
    render(<ObjectionLibrary />, { wrapper });
    fireEvent.click(screen.getByText('Add New'));
    expect(screen.getByText('Add New Objection')).toBeInTheDocument();
  });

  it('filters objections by search query', () => {
    render(<ObjectionLibrary />, { wrapper });
    const searchInput = screen.getByPlaceholderText('Search by objection text...');
    fireEvent.change(searchInput, { target: { value: 'expensive' } });
    expect(screen.getByText(mockObjection.objection)).toBeInTheDocument();
    
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } });
    expect(screen.queryByText(mockObjection.objection)).not.toBeInTheDocument();
  });

  it('filters objections by category', () => {
    render(<ObjectionLibrary />, { wrapper });
    fireEvent.click(screen.getByText('Competition'));
    expect(screen.queryByText(mockObjection.objection)).not.toBeInTheDocument();
    
    fireEvent.click(screen.getByText('Pricing'));
    expect(screen.getByText(mockObjection.objection)).toBeInTheDocument();
  });

  it('adds a new objection', async () => {
    render(<ObjectionLibrary />, { wrapper });
    
    // Open dialog
    fireEvent.click(screen.getByText('Add New'));
    
    // Fill form
    fireEvent.change(screen.getByLabelText('Objection'), {
      target: { value: 'New Objection' },
    });
    fireEvent.change(screen.getByLabelText('Response'), {
      target: { value: 'Test response' },
    });
    fireEvent.change(screen.getByLabelText('Category'), {
      target: { value: 'Technical' },
    });
    
    // Add a tag
    const tagInput = screen.getByLabelText('Add tags (press Enter)');
    fireEvent.change(tagInput, { target: { value: 'TestTag' } });
    fireEvent.keyDown(tagInput, { key: 'Enter' });
    
    // Save
    fireEvent.click(screen.getByText('Save'));
    
    // Verify new objection is displayed
    await waitFor(() => {
      expect(screen.getByText('New Objection')).toBeInTheDocument();
    });
  });

  it('edits an existing objection', async () => {
    render(<ObjectionLibrary />, { wrapper });
    
    // Click edit button
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    fireEvent.click(editButtons[0]);
    
    // Modify objection
    const objectionInput = screen.getByLabelText('Objection');
    fireEvent.change(objectionInput, { target: { value: 'Updated Objection' } });
    
    // Save
    fireEvent.click(screen.getByText('Save'));
    
    // Verify changes
    await waitFor(() => {
      expect(screen.getByText('Updated Objection')).toBeInTheDocument();
    });
  });

  it('deletes an objection', () => {
    render(<ObjectionLibrary />, { wrapper });
    
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    expect(screen.queryByText(mockObjection.objection)).not.toBeInTheDocument();
  });

  it('generates response using AI', async () => {
    render(<ObjectionLibrary />, { wrapper });
    
    // Open dialog
    fireEvent.click(screen.getByText('Add New'));
    
    // Enter objection
    fireEvent.change(screen.getByLabelText('Objection'), {
      target: { value: 'Test objection' },
    });
    
    // Click generate button
    fireEvent.click(screen.getByText('Generate'));
    
    // Verify loading state
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Verify generated content
    await waitFor(() => {
      expect(screen.getByLabelText('Response')).toHaveValue(
        expect.stringContaining('Based on our analysis')
      );
    });
  });

  it('validates required fields', async () => {
    render(<ObjectionLibrary />, { wrapper });
    
    // Open dialog
    fireEvent.click(screen.getByText('Add New'));
    
    // Try to save without filling required fields
    fireEvent.click(screen.getByText('Save'));
    
    // Verify error message
    expect(screen.getByText('Please fill in all required fields')).toBeInTheDocument();
  });

  it('handles tag management', () => {
    render(<ObjectionLibrary />, { wrapper });
    
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

  it('prevents generating response without objection', async () => {
    render(<ObjectionLibrary />, { wrapper });
    
    // Open dialog
    fireEvent.click(screen.getByText('Add New'));
    
    // Click generate without entering objection
    fireEvent.click(screen.getByText('Generate'));
    
    // Verify error message
    expect(screen.getByText('Please enter an objection first')).toBeInTheDocument();
  });
}); 
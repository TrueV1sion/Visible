import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom'; // If any sub-components use Link/useNavigate
import CustomerForm from './CustomerForm';
import { CustomerFormData } from '../../types/customer';

// Mock yup and resolver if not already globally mocked or to control its behavior
// For this test, we'll assume yup validation works as it's unit tested elsewhere or implicitly.
// We are more focused on the form component's interaction.

const mockSubmit = jest.fn();

const renderForm = (props: Partial<React.ComponentProps<typeof CustomerForm>> = {}) => {
  const defaultProps: React.ComponentProps<typeof CustomerForm> = {
    onSubmit: mockSubmit,
    initialData: null,
    isEditMode: false,
    isLoading: false,
    ...props,
  };
  return render(
    <BrowserRouter> {/* Wrapper in case any part of form/MUI uses routing context */}
      <CustomerForm {...defaultProps} />
    </BrowserRouter>
  );
};

describe('CustomerForm Component', () => {
  beforeEach(() => {
    mockSubmit.mockClear();
  });

  test('renders correctly in create mode', () => {
    renderForm();
    expect(screen.getByText(/Create New Customer/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Customer Name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Customer/i })).toBeInTheDocument();
  });

  test('renders correctly in edit mode with initial data', () => {
    const initialData: CustomerFormData = {
      name: 'Edit Test Payer',
      description: 'Payer for editing',
      business_model: 'PPO',
      membership_count: 5000,
      website_url: 'http://edit.example.com',
      primary_contact_name: 'Jane Edit',
      primary_contact_email: 'jane.edit@example.com',
      primary_contact_phone: '123-456-7890',
      notes: 'Some edit notes',
      quality_scores: [{ metric_name: 'Overall', score: 4, year: 2023, source: 'CMS' }],
      known_vendors: [{ name: 'EditVendor', service_provided: 'Claims', notes: 'Good' }],
    };
    renderForm({ initialData, isEditMode: true });

    expect(screen.getByText(/Edit Customer/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Customer Name/i)).toHaveValue(initialData.name);
    expect(screen.getByLabelText(/Description/i)).toHaveValue(initialData.description);
    expect(screen.getByRole('button', { name: /Save Changes/i })).toBeInTheDocument();

    // Check a quality score field
    expect(screen.getByLabelText(/Metric Name/i)).toHaveValue('Overall');
     // Check a vendor field
    expect(screen.getByLabelText(/Vendor Name/i)).toHaveValue('EditVendor');
  });

  test('allows typing in text fields', () => {
    renderForm();
    const nameInput = screen.getByLabelText(/Customer Name/i);
    fireEvent.change(nameInput, { target: { value: 'New Payer Name' } });
    expect(nameInput).toHaveValue('New Payer Name');

    const descriptionInput = screen.getByLabelText(/Description/i);
    fireEvent.change(descriptionInput, { target: { value: 'Test Description' } });
    expect(descriptionInput).toHaveValue('Test Description');
  });

  test('shows validation error for required fields (e.g., name)', async () => {
    renderForm();
    const submitButton = screen.getByRole('button', { name: /Create Customer/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      // Assumes yup validation shows a message containing "required" for the name field
      expect(screen.getByText(/Customer name is required/i)).toBeInTheDocument();
    });
  });

  test('calls onSubmit with form data when valid', async () => {
    renderForm();
    const nameInput = screen.getByLabelText(/Customer Name/i);
    fireEvent.change(nameInput, { target: { value: 'Valid Payer' } });

    const descriptionInput = screen.getByLabelText(/Description/i);
    fireEvent.change(descriptionInput, { target: { value: 'Valid Description' } });

    const membershipInput = screen.getByLabelText(/Membership Count/i);
    fireEvent.change(membershipInput, { target: { value: '12345' } });


    const submitButton = screen.getByRole('button', { name: /Create Customer/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledTimes(1);
      expect(mockSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Valid Payer',
          description: 'Valid Description',
          membership_count: 12345, // react-hook-form with yup schema should convert if input type="number"
          quality_scores: [], // Default empty arrays
          known_vendors: [],
        }),
        expect.anything() // For the event or form context
      );
    });
  });

  describe('Field Arrays', () => {
    test('can add and remove quality scores', async () => {
      renderForm();
      const addScoreButton = screen.getByRole('button', { name: /Add Quality Score/i });

      // Initially no score fields visible beyond the button
      expect(screen.queryByLabelText(/Metric Name/i)).not.toBeInTheDocument();

      fireEvent.click(addScoreButton);
      await screen.findByLabelText(/Metric Name/i); // Wait for it to appear
      expect(screen.getByLabelText(/Metric Name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Score/i)).toBeInTheDocument();

      // Fill the added score
      fireEvent.change(screen.getByLabelText(/Metric Name/i), { target: { value: 'HEDIS A' } });
      fireEvent.change(screen.getByLabelText(/Score/i), { target: { value: '90' } });

      // Add another one
      fireEvent.click(addScoreButton);
      const scoreFields = await screen.findAllByLabelText(/Metric Name/i);
      expect(scoreFields).toHaveLength(2);

      // Remove the first score
      const removeButtons = screen.getAllByRole('button', { name: /Remove quality score/i });
      fireEvent.click(removeButtons[0]);

      await waitFor(() => {
        const remainingScoreFields = screen.getAllByLabelText(/Metric Name/i);
        expect(remainingScoreFields).toHaveLength(1);
      });
      // Check if the correct one was removed (value should not be 'HEDIS A' if the first was removed)
      // This depends on the implementation; if the second one is now the first, its value will be empty.
      // A more robust check might involve checking the values of the remaining fields.
    });

    test('can add and remove vendors', async () => {
        renderForm();
        const addVendorButton = screen.getByRole('button', { name: /Add Vendor/i });

        expect(screen.queryByLabelText(/Vendor Name/i)).not.toBeInTheDocument();

        fireEvent.click(addVendorButton);
        await screen.findByLabelText(/Vendor Name/i);
        expect(screen.getByLabelText(/Vendor Name/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Service Provided/i)).toBeInTheDocument();

        fireEvent.change(screen.getByLabelText(/Vendor Name/i), { target: { value: 'ClaimsRUs' } });

        const removeButtons = screen.getAllByRole('button', { name: /Remove vendor/i });
        fireEvent.click(removeButtons[0]);

        await waitFor(() => {
            expect(screen.queryByLabelText(/Vendor Name/i)).not.toBeInTheDocument();
        });
    });
  });

  test('isLoading prop disables submit button', () => {
    renderForm({ isLoading: true });
    const submitButton = screen.getByRole('button', { name: /Create Customer/i });
    expect(submitButton).toBeDisabled();
  });

});

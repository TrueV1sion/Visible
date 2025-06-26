import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Alert, Box, CircularProgress } from '@mui/material';
import CustomerForm from '../components/customers/CustomerForm';
import { CustomerFormData } from '../types/customer';
import { createCustomer } from '../api/customers';

const CreateCustomerPage: React.FC = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (data: CustomerFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      // Convert empty strings for optional numbers to undefined if necessary,
      // though yup schema with .nullable().typeError() should handle some of this.
      // The CustomerFormData type might need refinement if numbers are strings from form.
      const payload = {
        ...data,
        membership_count: data.membership_count === undefined || data.membership_count === null || isNaN(Number(data.membership_count))
          ? undefined
          : Number(data.membership_count),
        // Ensure quality_scores and known_vendors are arrays
        quality_scores: data.quality_scores || [],
        known_vendors: data.known_vendors || [],
      };

      const newCustomer = await createCustomer(payload);
      // TODO: Add success notification (e.g., using ToastProvider from frontend/src/providers/ToastProvider.tsx)
      navigate(`/customers/${newCustomer.id}`); // Navigate to the new customer's detail page (to be created)
                                                // Or navigate back to customer list: navigate('/customers');
    } catch (err: any) {
      console.error('Failed to create customer:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to create customer. Please try again.');
      setIsLoading(false);
    }
    // No finally setIsLoading(false) here as navigation occurs on success
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Create New Customer
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      )}
      <CustomerForm onSubmit={handleSubmit} isLoading={isLoading} />
    </Container>
  );
};

export default CreateCustomerPage;

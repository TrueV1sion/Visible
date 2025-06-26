import React, { useState, useEffect } from 'react';
import { useNavigate, useParams }_from 'react-router-dom';
import { Container, Typography, Alert, CircularProgress, Box } from '@mui/material';
import CustomerForm from '../components/customers/CustomerForm';
import { Customer, CustomerFormData, CustomerUpdate } from '../types/customer';
import { getCustomerById, updateCustomer } from '../api/customers';

const EditCustomerPage: React.FC = () => {
  const navigate = useNavigate();
  const { customerId } = useParams<{ customerId: string }>();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false); // For submission
  const [isFetching, setIsFetching] = useState<boolean>(true); // For initial data fetch

  useEffect(() => {
    if (!customerId) {
      setError('Customer ID is missing.');
      setIsFetching(false);
      return;
    }

    const fetchCustomer = async () => {
      setIsFetching(true);
      setError(null);
      try {
        const data = await getCustomerById(Number(customerId));
        setCustomer(data);
      } catch (err: any) {
        console.error('Failed to fetch customer:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to fetch customer data.');
      } finally {
        setIsFetching(false);
      }
    };
    fetchCustomer();
  }, [customerId]);

  const handleSubmit = async (data: CustomerFormData) => {
    if (!customerId) {
      setError('Customer ID is missing for update.');
      return;
    }
    setIsLoading(true);
    setError(null);

    // Construct the CustomerUpdate payload. It should only contain fields that are being updated.
    // However, our form submits all fields. The backend Pydantic model for update (CustomerUpdate)
    // should have all fields as Optional.
    // If the API expects only changed fields, more complex logic is needed here to diff initialData and current data.
    // For now, sending all fields as per CustomerUpdate schema.
    const updatePayload: CustomerUpdate = {
        ...data,
        membership_count: data.membership_count === undefined || data.membership_count === null || isNaN(Number(data.membership_count))
          ? undefined
          : Number(data.membership_count),
        quality_scores: data.quality_scores || [],
        known_vendors: data.known_vendors || [],
    };


    try {
      await updateCustomer(Number(customerId), updatePayload);
      // TODO: Add success notification
      navigate(`/customers/${customerId}`); // Navigate to the customer's detail page
                                            // Or navigate back to customer list: navigate('/customers');
    } catch (err: any) {
      console.error('Failed to update customer:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to update customer. Please try again.');
      setIsLoading(false);
    }
  };

  if (isFetching) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading customer data...</Typography>
      </Container>
    );
  }

  if (error && !customer) { // If there was an error fetching and no customer data
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!customer) { // Should not happen if no error and fetching is done, but as a safeguard
     return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="warning">Customer data not available.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Edit Customer
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
      {isLoading && ( // Loading state for submission
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      )}
      <CustomerForm
        onSubmit={handleSubmit}
        initialData={customer}
        isEditMode={true}
        isLoading={isLoading}
      />
    </Container>
  );
};

export default EditCustomerPage;

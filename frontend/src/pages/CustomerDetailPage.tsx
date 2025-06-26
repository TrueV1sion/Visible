import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Box,
  Grid,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Business as BusinessIcon,
  PeopleAlt as PeopleAltIcon,
  Link as LinkIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Notes as NotesIcon,
  StarBorder as StarBorderIcon, // For Quality Scores
  Handshake as HandshakeIcon, // For Vendors
  Edit as EditIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material';
import { Customer } from '../types/customer';
import { getCustomerById } from '../api/customers';

const DetailItem: React.FC<{ icon: React.ReactElement; primary: string; secondary?: string | number | null }> = ({ icon, primary, secondary }) => (
  secondary ? (
    <ListItem>
      <ListItemIcon sx={{minWidth: '40px'}}>{icon}</ListItemIcon>
      <ListItemText primary={primary} secondary={secondary} />
    </ListItem>
  ) : null
);

const CustomerDetailPage: React.FC = () => {
  const { customerId } = useParams<{ customerId: string }>();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!customerId) {
      setError('Customer ID is missing.');
      setLoading(false);
      return;
    }
    const fetchCustomer = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getCustomerById(Number(customerId));
        setCustomer(data);
      } catch (err: any) {
        console.error('Failed to fetch customer:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to fetch customer details.');
      } finally {
        setLoading(false);
      }
    };
    fetchCustomer();
  }, [customerId]);

  if (loading) {
    return (
      <Container sx={{ textAlign: 'center', mt: 5 }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading customer details...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 5 }}>
        <Alert severity="error">{error}</Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/customers')} sx={{ mt: 2 }}>
          Back to Customers List
        </Button>
      </Container>
    );
  }

  if (!customer) {
    return (
      <Container sx={{ mt: 5 }}>
        <Alert severity="warning">Customer not found.</Alert>
         <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/customers')} sx={{ mt: 2 }}>
          Back to Customers List
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {customer.name}
          </Typography>
          <Box>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/customers')}
              sx={{ mr: 1 }}
            >
              Back to List
            </Button>
            <Button
              variant="contained"
              startIcon={<EditIcon />}
              onClick={() => navigate(`/customers/${customer.id}/edit`)}
            >
              Edit Customer
            </Button>
          </Box>
        </Box>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>Customer Information</Typography>
            <List dense>
              <DetailItem icon={<BusinessIcon />} primary="Business Model" secondary={customer.business_model} />
              <DetailItem icon={<PeopleAltIcon />} primary="Membership Count" secondary={customer.membership_count?.toLocaleString()} />
              {customer.website_url && (
                <ListItem>
                  <ListItemIcon sx={{minWidth: '40px'}}><LinkIcon /></ListItemIcon>
                  <ListItemText primary="Website" secondary={<a href={customer.website_url} target="_blank" rel="noopener noreferrer">{customer.website_url}</a>} />
                </ListItem>
              )}
              <DetailItem icon={<EmailIcon />} primary="Primary Contact Email" secondary={customer.primary_contact_email} />
              <DetailItem icon={<PhoneIcon />} primary="Primary Contact Phone" secondary={customer.primary_contact_phone} />
              <DetailItem icon={<NotesIcon />} primary="Description" secondary={customer.description} />
            </List>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>Quality Scores</Typography>
            {customer.quality_scores && customer.quality_scores.length > 0 ? (
              <List dense>
                {customer.quality_scores.map((qs, index) => (
                  <ListItem key={index} divider>
                    <ListItemIcon sx={{minWidth: '40px'}}><StarBorderIcon /></ListItemIcon>
                    <ListItemText
                      primary={`${qs.metric_name}: ${qs.score}`}
                      secondary={`Year: ${qs.year || 'N/A'}, Source: ${qs.source || 'N/A'}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">No quality scores available.</Typography>
            )}

            <Typography variant="h6" gutterBottom sx={{mt: 3}}>Known Vendors</Typography>
            {customer.known_vendors && customer.known_vendors.length > 0 ? (
               <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt:1 }}>
                {customer.known_vendors.map((vendor, index) => (
                   <Chip
                    key={index}
                    icon={<HandshakeIcon />}
                    label={vendor.name}
                    title={`${vendor.service_provided || ''} ${vendor.notes || ''}`}
                    variant="outlined"
                  />
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">No known vendors listed.</Typography>
            )}
          </Grid>

          {customer.notes && (
            <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{mt:2}}>General Notes</Typography>
                <Paper variant="outlined" sx={{p:2, whiteSpace: 'pre-wrap', backgroundColor: '#f9f9f9'}}>
                    {customer.notes}
                </Paper>
            </Grid>
          )}
        </Grid>

        <Divider sx={{ my: 3 }} />
        <Typography variant="caption" color="text.secondary">
          Last Updated: {new Date(customer.updated_at).toLocaleString()}
        </Typography>
      </Paper>
    </Container>
  );
};

export default CustomerDetailPage;

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Menu,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
} from '@mui/material';
import { Add as AddIcon, MoreVert as MoreVertIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { Customer } from '../types/customer';
import { getCustomers, deleteCustomer as apiDeleteCustomer } from '../api/customers'; // Renamed to avoid conflict

const CustomersPage: React.FC = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [actionAnchorEl, setActionAnchorEl] = useState<{ [key: number]: HTMLElement | null }>({});

  const fetchCustomersList = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // TODO: Implement proper pagination in API call if backend supports it fully for getCustomers
      // For now, fetching all and slicing, or assuming API handles skip/limit correctly
      const data = await getCustomers(page * rowsPerPage, rowsPerPage);
      setCustomers(data);
      // If API doesn't return total count for pagination, we might need another endpoint or adjust logic
    } catch (err) {
      setError('Failed to fetch customers. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage]);

  useEffect(() => {
    fetchCustomersList();
  }, [fetchCustomersList]);

  const handleActionClick = (event: React.MouseEvent<HTMLElement>, customerId: number) => {
    setActionAnchorEl({ ...actionAnchorEl, [customerId]: event.currentTarget });
  };

  const handleActionClose = (customerId: number) => {
    setActionAnchorEl({ ...actionAnchorEl, [customerId]: null });
  };

  const handleEdit = (customerId: number) => {
    navigate(`/customers/${customerId}/edit`);
    handleActionClose(customerId);
  };

  const handleDelete = async (customerId: number) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        await apiDeleteCustomer(customerId);
        setCustomers(customers.filter(c => c.id !== customerId));
        // Optionally show a success notification
      } catch (err) {
        setError('Failed to delete customer.');
        console.error(err);
        // Optionally show an error notification
      }
    }
    handleActionClose(customerId);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Health Plan/Payer Customers</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/customers/new')}
        >
          Create Customer
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer>
          <Table stickyHeader aria-label="customers table">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Business Model</TableCell>
                <TableCell>Membership Count</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {customers
                // .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage) // Client-side pagination if API doesn't support it well
                .map((customer) => (
                <TableRow hover role="checkbox" tabIndex={-1} key={customer.id}>
                  <TableCell component="th" scope="row">
                    {customer.name}
                  </TableCell>
                  <TableCell>{customer.business_model || 'N/A'}</TableCell>
                  <TableCell>{customer.membership_count?.toLocaleString() || 'N/A'}</TableCell>
                  <TableCell>{new Date(customer.updated_at).toLocaleDateString()}</TableCell>
                  <TableCell align="right">
                    <IconButton onClick={(e) => handleActionClick(e, customer.id)} size="small">
                      <MoreVertIcon />
                    </IconButton>
                    <Menu
                      anchorEl={actionAnchorEl[customer.id]}
                      open={Boolean(actionAnchorEl[customer.id])}
                      onClose={() => handleActionClose(customer.id)}
                    >
                      <MenuItem onClick={() => navigate(`/customers/${customer.id}`)}>View Details</MenuItem>
                      <MenuItem onClick={() => handleEdit(customer.id)}>
                        <EditIcon fontSize="small" sx={{ mr: 1 }} /> Edit
                      </MenuItem>
                      <MenuItem onClick={() => handleDelete(customer.id)}>
                        <DeleteIcon fontSize="small" sx={{ mr: 1 }} /> Delete
                      </MenuItem>
                    </Menu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 100]}
          component="div"
          count={customers.length} // TODO: This should be total count from API for server-side pagination
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
};

export default CustomersPage;

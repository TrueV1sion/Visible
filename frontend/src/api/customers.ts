import { api } from './client'; // Assuming 'api' is the exported Axios instance from client.ts
import { Customer, CustomerCreate, CustomerUpdate } from '../types/customer';

const CUSTOMERS_ENDPOINT = '/api/v1/customers'; // Matches backend router prefix

export const getCustomers = async (skip: number = 0, limit: number = 100): Promise<Customer[]> => {
  try {
    const response = await api.get<Customer[]>(`${CUSTOMERS_ENDPOINT}/`, {
      params: { skip, limit },
    });
    return response; // Axios already returns response.data due to our ApiClient setup
  } catch (error) {
    console.error('Error fetching customers:', error);
    throw error; // Re-throw to allow calling component to handle
  }
};

export const getCustomerById = async (customerId: number): Promise<Customer> => {
  try {
    const response = await api.get<Customer>(`${CUSTOMERS_ENDPOINT}/${customerId}`);
    return response;
  } catch (error) {
    console.error(`Error fetching customer ${customerId}:`, error);
    throw error;
  }
};

export const createCustomer = async (customerData: CustomerCreate): Promise<Customer> => {
  try {
    const response = await api.post<Customer>(`${CUSTOMERS_ENDPOINT}/`, customerData);
    return response;
  } catch (error) {
    console.error('Error creating customer:', error);
    throw error;
  }
};

export const updateCustomer = async (
  customerId: number,
  customerData: CustomerUpdate,
): Promise<Customer> => {
  try {
    const response = await api.put<Customer>(`${CUSTOMERS_ENDPOINT}/${customerId}`, customerData);
    return response;
  } catch (error) {
    console.error(`Error updating customer ${customerId}:`, error);
    throw error;
  }
};

export const deleteCustomer = async (customerId: number): Promise<Customer> => {
  // Backend returns the deleted customer object, adjust if it only returns status
  try {
    const response = await api.delete<Customer>(`${CUSTOMERS_ENDPOINT}/${customerId}`);
    return response;
  } catch (error) {
    console.error(`Error deleting customer ${customerId}:`, error);
    throw error;
  }
};

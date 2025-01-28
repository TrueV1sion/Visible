import { AxiosError } from 'axios';
import { api } from './api';

export interface ProductSegment {
  id: string;
  name: string;
  description: string;
  marketSize?: number;
  growthRate?: number;
  keyFeatures: string[];
}

export const fetchProductSegments = async (): Promise<ProductSegment[]> => {
  try {
    const response = await api.get<ProductSegment[]>('/api/product-segments');
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
};

export const fetchProductSegment = async (id: string): Promise<ProductSegment> => {
  try {
    const response = await api.get<ProductSegment>(`/api/product-segments/${id}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
}; 
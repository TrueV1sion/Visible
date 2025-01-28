import { AxiosError } from 'axios';
import { api } from './api';

export interface Objection {
  id: string;
  objection: string;
  response: string;
  category: string;
  effectiveness: number;
  usageCount: number;
}

export const fetchObjections = async (): Promise<Objection[]> => {
  try {
    const response = await api.get<Objection[]>('/api/objections');
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
}; 
import { AxiosError } from 'axios';
import { api } from './api';

export interface Competitor {
  id: string;
  name: string;
  website: string;
  description: string;
  marketShare?: number;
  founded?: string;
  headquarters?: string;
}

export interface CompetitorUpdate {
  id: string;
  competitor: string;
  type: 'feature' | 'pricing' | 'market' | 'product';
  change: string;
  impact: 'positive' | 'negative' | 'neutral';
  date: string;
  details: string;
}

export const fetchCompetitors = async (): Promise<Competitor[]> => {
  try {
    const response = await api.get<Competitor[]>('/api/competitors');
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
};

export const fetchCompetitor = async (id: string): Promise<Competitor> => {
  try {
    const response = await api.get<Competitor>(`/api/competitors/${id}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
};

export const fetchCompetitorUpdates = async (): Promise<CompetitorUpdate[]> => {
  try {
    const response = await api.get<CompetitorUpdate[]>('/api/competitors/updates');
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
}; 
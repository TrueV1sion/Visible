import { AxiosError } from 'axios';
import { api } from './api';

export interface Battlecard {
  id: string;
  title: string;
  competitor: string;
  lastUpdated: string;
  status: 'draft' | 'published' | 'archived';
  overview: string;
  differentiators: string;
  advantages: string;
  customNotes?: string;
}

export interface BattlecardInput {
  productSegment: string;
  competitor: string;
  customNotes?: string;
}

export const fetchBattlecards = async (): Promise<Battlecard[]> => {
  try {
    const response = await api.get<Battlecard[]>('/api/battlecards');
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
};

export const fetchBattlecard = async (id: string): Promise<Battlecard> => {
  try {
    const response = await api.get<Battlecard>(`/api/battlecards/${id}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
};

export const generateBattlecard = async (input: BattlecardInput): Promise<Battlecard> => {
  try {
    const response = await api.post<Battlecard>('/api/battlecards/generate', input);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
};

export const updateBattlecard = async (id: string, data: Partial<Battlecard>): Promise<Battlecard> => {
  try {
    const response = await api.put<Battlecard>(`/api/battlecards/${id}`, data);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
};

export const deleteBattlecard = async (id: string): Promise<void> => {
  try {
    await api.delete(`/api/battlecards/${id}`);
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
}; 
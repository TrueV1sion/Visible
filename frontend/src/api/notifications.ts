import { AxiosError } from 'axios';
import { api } from './api';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'competitor' | 'battlecard' | 'marketing' | 'feature';
  timestamp: string;
  read: boolean;
}

export const fetchNotifications = async (): Promise<Notification[]> => {
  try {
    const response = await api.get<Notification[]>('/api/notifications');
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
};

export const markAsRead = async (id: string): Promise<void> => {
  try {
    await api.put(`/api/notifications/${id}/read`);
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(axiosError.message);
  }
}; 
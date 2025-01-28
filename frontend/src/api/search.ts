import { AxiosError } from 'axios';
import { api } from './api';

export interface SearchFilters {
  productLines: string[];
  competitors: string[];
  dateRange: 'all' | 'week' | 'month' | 'quarter' | 'year';
  type: 'all' | 'battlecard' | 'competitor' | 'objection';
}

export interface SearchResult {
  id: string;
  title: string;
  excerpt: string;
  type: 'battlecard' | 'competitor' | 'objection';
  tags: string[];
  relevanceScore: number;
  lastUpdated: string;
}

export const searchBattlecards = async (
  query: string,
  filters: SearchFilters
): Promise<SearchResult[]> => {
  try {
    // Convert the query into a vector using the backend's embedding service
    const response = await api.post<SearchResult[]>('/api/search', {
      query,
      filters,
      options: {
        useSemanticSearch: true,
        minRelevanceScore: 0.7,
        limit: 20,
      },
    });

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(
      `Failed to perform search: ${axiosError.message}`
    );
  }
};

export const getRecentSearches = async (): Promise<string[]> => {
  try {
    const response = await api.get<string[]>('/api/search/recent');
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(
      `Failed to fetch recent searches: ${axiosError.message}`
    );
  }
};

export const getSuggestedSearches = async (
  partialQuery: string
): Promise<string[]> => {
  try {
    const response = await api.get<string[]>('/api/search/suggestions', {
      params: { query: partialQuery },
    });
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(
      `Failed to fetch search suggestions: ${axiosError.message}`
    );
  }
};

export const saveSearchQuery = async (query: string): Promise<void> => {
  try {
    await api.post('/api/search/history', { query });
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(
      `Failed to save search query: ${axiosError.message}`
    );
  }
}; 
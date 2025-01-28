import { AxiosError } from 'axios';
import { api } from './api';

export type InsightType = 
  | 'competitive_advantage'
  | 'market_trend'
  | 'pricing_strategy'
  | 'feature_comparison'
  | 'customer_feedback'
  | 'sales_objection';

export interface InsightContext {
  battlecardId?: string;
  competitorId?: string;
  productId?: string;
  section?: string;
}

export interface InsightSuggestion {
  id: string;
  type: InsightType;
  content: string;
  confidence: number;
  sources: string[];
  suggestedActions: string[];
  timestamp: string;
  metadata?: {
    relevantBattlecards?: string[];
    competitorMentions?: string[];
    marketSegments?: string[];
  };
}

export const generateInsights = async (
  context: InsightContext
): Promise<InsightSuggestion[]> => {
  try {
    const response = await api.post<InsightSuggestion[]>(
      '/api/v1/ai/insights/generate',
      {
        input_data: {
          context,
          options: {
            minConfidence: 0.6,
            maxResults: 5,
            includeSourceReferences: true,
          },
        },
      }
    );
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(
      `Failed to generate insights: ${axiosError.message}`
    );
  }
};

export const applyInsight = async (
  insightId: string,
  battlecardId: string
): Promise<void> => {
  try {
    await api.post('/api/v1/ai/insights/apply', {
      insight_id: insightId,
      target_battlecard_id: battlecardId,
    });
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(
      `Failed to apply insight: ${axiosError.message}`
    );
  }
};

export const discardInsight = async (
  insightId: string
): Promise<void> => {
  try {
    await api.post('/api/v1/ai/insights/discard', {
      insight_id: insightId,
    });
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(
      `Failed to discard insight: ${axiosError.message}`
    );
  }
};

export const getInsightHistory = async (
  context: InsightContext
): Promise<InsightSuggestion[]> => {
  try {
    const response = await api.get<InsightSuggestion[]>('/api/insights/history', {
      params: context,
    });
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError;
    throw new Error(
      `Failed to fetch insight history: ${axiosError.message}`
    );
  }
}; 
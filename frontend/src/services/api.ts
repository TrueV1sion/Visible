import { apiClient } from '../api/client';

// Type definitions
export interface Battlecard {
  id: string;
  title: string;
  description?: string;
  status: 'draft' | 'review' | 'published' | 'archived';
  competitor?: {
    id: string;
    name: string;
    website?: string;
  };
  content: {
    overview?: any;
    strengths_weaknesses?: any;
    objection_handling?: any;
    winning_strategies?: any;
  };
  created_at: string;
  updated_at?: string;
  created_by: {
    id: string;
    name: string;
    email: string;
  };
}

export interface BattlecardGenerationRequest {
  competitor_info: {
    name: string;
    website?: string;
    description?: string;
    primary_offering?: string;
    target_market?: string;
  };
  product_segment: string;
  focus_areas: string[];
  include_sections?: string[];
}

export interface AIProcessingOptions {
  model_preference?: 'claude' | 'gpt' | 'auto';
  complexity_level?: 'low' | 'medium' | 'high';
  max_tokens?: number;
  temperature?: number;
  include_sources?: boolean;
}

export interface CompetitorUpdate {
  id: string;
  competitor: string;
  title: string;
  description: string;
  type: 'pricing' | 'product' | 'market' | 'feature';
  impact_level: 'high' | 'medium' | 'low';
  ai_insights?: string;
  suggested_actions?: string[];
  sources?: string[];
  update_date: string;
  created_at: string;
}

// Battlecard service
export const battlecardService = {
  // List battlecards with filtering
  async list(filters: {
    status?: string;
    competitor?: string;
    skip?: number;
    limit?: number;
  } = {}): Promise<Battlecard[]> {
    return apiClient.get('/battlecards', { params: filters });
  },

  // Get single battlecard
  async get(id: string): Promise<Battlecard> {
    return apiClient.get(`/battlecards/${id}`);
  },

  // Generate battlecard with AI
  async generate(
    request: BattlecardGenerationRequest,
    options?: AIProcessingOptions
  ): Promise<Battlecard> {
    const payload = {
      ...request,
      ai_options: options
    };
    
    return apiClient.post('/battlecards/generate', payload);
  },

  // Update battlecard
  async update(id: string, data: Partial<Battlecard>): Promise<Battlecard> {
    return apiClient.put(`/battlecards/${id}`, data);
  },

  // Delete battlecard
  async delete(id: string): Promise<void> {
    return apiClient.delete(`/battlecards/${id}`);
  },

  // Regenerate specific section
  async regenerateSection(
    id: string, 
    section: string, 
    options?: AIProcessingOptions
  ): Promise<{ status: string; content: any; version: number }> {
    return apiClient.post(`/battlecards/${id}/regenerate-section`, {
      section,
      options
    });
  },

  // Get AI status
  async getAIStatus(): Promise<{
    active_requests: number;
    max_concurrent: number;
    available_agents: string[];
    cache_stats: any;
  }> {
    return apiClient.get('/battlecards/ai/status');
  }
};

// Competitor service
export const competitorService = {
  async list(): Promise<any[]> {
    return apiClient.get('/competitors');
  },

  async getUpdates(): Promise<CompetitorUpdate[]> {
    return apiClient.get('/competitors/updates');
  },

  async monitor(competitorId: string): Promise<any> {
    return apiClient.post(`/ai/aggregator/monitor`, { competitor_id: competitorId });
  }
};

// Objection service
export const objectionService = {
  async list(filters: { category?: string } = {}): Promise<any[]> {
    return apiClient.get('/objections', { params: filters });
  },

  async generateResponse(
    objection: string, 
    context: any = {}
  ): Promise<{ response: string; evidence: string[] }> {
    return apiClient.post('/ai/objection-handling', {
      input_data: {
        objection,
        context
      }
    });
  }
};

// Auth service
export const authService = {
  async login(email: string, password: string): Promise<{
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  }> {
    const response = await apiClient.post('/auth/login', {
      username: email,
      password
    });
    
    // Store tokens
    localStorage.setItem('authToken', response.access_token);
    localStorage.setItem('refreshToken', response.refresh_token);
    
    return response;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      // Always clear local storage
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
    }
  },

  async getCurrentUser(): Promise<any> {
    return apiClient.get('/users/me');
  },

  async validateToken(): Promise<{ valid: boolean; expires_in: number }> {
    return apiClient.post('/auth/validate-token');
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    return apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }
};

// Search service
export const searchService = {
  async search(query: string, filters: any = {}): Promise<any[]> {
    return apiClient.get('/search', { 
      params: { query, ...filters } 
    });
  },

  async getRecentSearches(): Promise<string[]> {
    return apiClient.get('/search/recent');
  }
};

// Insights service
export const insightsService = {
  async generate(context: any): Promise<any[]> {
    return apiClient.post('/ai/insights/generate', {
      input_data: context
    });
  },

  async apply(insightId: string, battlecardId: string): Promise<void> {
    return apiClient.post('/ai/insights/apply', {
      insight_id: insightId,
      target_battlecard_id: battlecardId
    });
  },

  async discard(insightId: string): Promise<void> {
    return apiClient.post('/ai/insights/discard', {
      insight_id: insightId
    });
  }
};

// Analytics service
export const analyticsService = {
  async getDashboardStats(): Promise<{
    total_battlecards: number;
    active_competitors: number;
    ai_generation_usage: number;
    user_activity: any;
  }> {
    return apiClient.get('/analytics/dashboard');
  },

  async getUsageMetrics(period: string = '30d'): Promise<any> {
    return apiClient.get('/analytics/usage', { params: { period } });
  }
};
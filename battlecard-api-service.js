// src/services/battlecardService.js
import axios from 'axios';

// Configure API base URLs
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const AI_API_URL = process.env.REACT_APP_AI_API_URL || 'http://localhost:8000/api/v1/ai';

// Create axios instances with interceptors
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const aiApi = axios.create({
  baseURL: AI_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
const setupInterceptors = () => {
  const requestInterceptor = (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  };

  api.interceptors.request.use(requestInterceptor);
  aiApi.interceptors.request.use(requestInterceptor);

  // Response interceptors for handling common errors
  const responseErrorInterceptor = (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  };

  api.interceptors.response.use(
    (response) => response,
    responseErrorInterceptor
  );

  aiApi.interceptors.response.use(
    (response) => response,
    responseErrorInterceptor
  );
};

setupInterceptors();

// Battlecard API Service
const battlecardService = {
  // Core battlecard operations
  fetchBattlecards: async (filters = {}) => {
    try {
      const response = await api.get('/battlecards', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching battlecards:', error);
      throw error;
    }
  },

  fetchBattlecard: async (id) => {
    try {
      const response = await api.get(`/battlecards/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching battlecard ${id}:`, error);
      throw error;
    }
  },

  createBattlecard: async (data) => {
    try {
      const response = await api.post('/battlecards', data);
      return response.data;
    } catch (error) {
      console.error('Error creating battlecard:', error);
      throw error;
    }
  },

  updateBattlecard: async (id, data) => {
    try {
      const response = await api.put(`/battlecards/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating battlecard ${id}:`, error);
      throw error;
    }
  },

  deleteBattlecard: async (id) => {
    try {
      const response = await api.delete(`/battlecards/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting battlecard ${id}:`, error);
      throw error;
    }
  },

  // AI-powered battlecard generation
  generateBattlecard: async (input) => {
    try {
      const response = await aiApi.post('/aggregator/process', {
        competitor_name: input.competitor_info.name,
        search_terms: [
          `${input.competitor_info.name} company`,
          `${input.competitor_info.name} ${input.competitor_info.primary_offering || ''}`,
          `${input.competitor_info.name} vs`
        ],
        context: {
          product_segment: input.product_segment,
          focus_areas: input.focus_areas
        }
      });

      // If successful, create a battlecard from the generated data
      if (response.data.status === 'success') {
        const battlecardData = {
          title: `${input.competitor_info.name} Battlecard`,
          description: `Competitive analysis for ${input.competitor_info.name}`,
          competitor_info: input.competitor_info,
          product_segment: input.product_segment,
          content: response.data.data,
          ai_generated: true,
          ai_model_used: response.data.metadata?.model_used || 'unknown'
        };

        return await battlecardService.createBattlecard(battlecardData);
      } else {
        throw new Error(response.data.error || 'Generation failed');
      }
    } catch (error) {
      console.error('Error generating battlecard:', error);
      throw error;
    }
  },

  // Regenerate specific section of a battlecard
  regenerateSection: async (battlecardId, sectionId, context = {}) => {
    try {
      // First fetch the battlecard to get context data
      const battlecard = await battlecardService.fetchBattlecard(battlecardId);
      
      // Map section ID to prompt type
      const sectionToPromptType = {
        'overview': 'battlecard_overview',
        'strengths_weaknesses': 'strengths_weaknesses',
        'competitive_analysis': 'competitive_analysis',
        'objection_handling': 'objection_handling',
        'pricing_comparison': 'pricing_comparison',
        'winning_strategies': 'winning_strategies'
      };

      const promptType = sectionToPromptType[sectionId] || 'custom';
      
      // Call AI service with section-specific endpoint
      const response = await aiApi.post(`/content-analysis`, {
        input_data: {
          battlecard_id: battlecardId,
          section_id: sectionId,
          prompt_type: promptType,
          competitor_info: battlecard.competitor_info,
          context: {
            ...context,
            product_segment: battlecard.product_segment
          }
        }
      });

      if (response.data.status === 'success') {
        // Update only the specific section
        const updatedContent = {
          ...battlecard.content,
          [sectionId]: response.data.data.content
        };
        
        // Update the battlecard with the new section content
        return await battlecardService.updateBattlecard(battlecardId, {
          content: updatedContent,
          last_ai_update: new Date().toISOString()
        });
      } else {
        throw new Error(response.data.error || `Failed to regenerate ${sectionId}`);
      }
    } catch (error) {
      console.error(`Error regenerating section ${sectionId}:`, error);
      throw error;
    }
  },

  // Competitor operations
  fetchCompetitors: async () => {
    try {
      const response = await api.get('/competitors');
      return response.data;
    } catch (error) {
      console.error('Error fetching competitors:', error);
      throw error;
    }
  },

  fetchCompetitorUpdates: async () => {
    try {
      const response = await api.get('/competitors/updates');
      return response.data;
    } catch (error) {
      console.error('Error fetching competitor updates:', error);
      throw error;
    }
  },

  // Monitor a competitor for changes
  monitorCompetitor: async (competitorId) => {
    try {
      const response = await aiApi.post('/aggregator/monitor', { competitor_id: competitorId });
      return response.data;
    } catch (error) {
      console.error(`Error monitoring competitor ${competitorId}:`, error);
      throw error;
    }
  },

  // Objection handling operations
  fetchObjections: async (filters = {}) => {
    try {
      const response = await api.get('/objections', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching objections:', error);
      throw error;
    }
  },

  generateObjectionResponse: async (objection, context = {}) => {
    try {
      const response = await aiApi.post('/objection-handling', {
        input_data: {
          objection: objection,
          context: context
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error generating objection response:', error);
      throw error;
    }
  },

  // Search operations
  search: async (query, filters = {}) => {
    try {
      const response = await api.get('/search', {
        params: {
          q: query,
          ...filters
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching:', error);
      throw error;
    }
  },

  // Analytics operations
  fetchAnalytics: async (period = '30d') => {
    try {
      const response = await api.get('/analytics', {
        params: { period }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics:', error);
      throw error;
    }
  },

  // User operations
  fetchCurrentUser: async () => {
    try {
      const response = await api.get('/users/me');
      return response.data;
    } catch (error) {
      console.error('Error fetching current user:', error);
      throw error;
    }
  },

  // Advanced use cases for specific sections
  generateUseCase: async (customerData, solutionDetails) => {
    try {
      const response = await aiApi.post('/use-case', {
        input_data: {
          customer_data: customerData,
          solution_details: solutionDetails
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error generating use case:', error);
      throw error;
    }
  },

  // Insights generation
  generateInsights: async (context) => {
    try {
      const response = await aiApi.post('/insights/generate', {
        input_data: context
      });
      return response.data;
    } catch (error) {
      console.error('Error generating insights:', error);
      throw error;
    }
  },

  // Apply insight to a battlecard
  applyInsight: async (insightId, battlecardId) => {
    try {
      const response = await aiApi.post('/insights/apply', {
        insight_id: insightId,
        target_battlecard_id: battlecardId
      });
      return response.data;
    } catch (error) {
      console.error('Error applying insight:', error);
      throw error;
    }
  },

  // Mock API for development
  _mockGenerateBattlecard: async (input) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Mock response
    return {
      id: 'bc-' + Date.now(),
      title: `${input.competitor_info.name} Battlecard`,
      description: `Competitive analysis for ${input.competitor_info.name}`,
      competitor_info: input.competitor_info,
      product_segment: input.product_segment,
      content: {
        metadata: {
          generated_at: new Date().toISOString(),
          competitor: input.competitor_info.name
        },
        overview: {
          company_name: input.competitor_info.name,
          description: `${input.competitor_info.name} is a leading provider of ${input.competitor_info.primary_offering || 'cloud solutions'} focusing on ${input.competitor_info.target_market || 'enterprise'} organizations.`,
          key_metrics: {
            founded: '2015',
            employees: '500+',
            funding: '$120M Series C (2023)'
          },
          target_market: ['Enterprise customers', 'Mid-market organizations', 'Healthcare sector'],
          recent_developments: [
            'Launched new AI-powered analytics platform',
            'Expanded operations to European market',
            'Acquired data visualization startup'
          ]
        },
        strengths_weaknesses: {
          strengths: [
            'Strong brand recognition',
            'Extensive enterprise customer base',
            'Robust feature set',
            'Well-established partner ecosystem'
          ],
          weaknesses: [
            'Higher pricing',
            'Complex implementation process',
            'Limited customization options',
            'Slower release cycle'
          ],
          opportunities: [
            'Gaps in customer support',
            'Missing key integrations',
            'Slow to adopt AI/ML capabilities'
          ],
          threats: [
            'Rapidly gaining market share',
            'Strong executive relationships',
            'Aggressive pricing strategies'
          ]
        },
        objection_handling: {
          objections: [
            {
              objection: `${input.competitor_info.name} is cheaper than your solution`,
              response: 'While their initial price point may appear lower, our total cost of ownership is typically 20% less over a three-year period due to our all-inclusive pricing model that avoids hidden fees and surcharges.',
              evidence: ['ROI calculator showing 3-year TCO', 'Case study: Company X saved $430K']
            },
            {
              objection: `${input.competitor_info.name} has more features than your product`,
              response: 'Our platform focuses on delivering the core features that drive 95% of customer value with superior quality and performance, rather than including rarely-used capabilities that add complexity and performance overhead.',
              evidence: ['Feature utilization analysis', 'Customer survey results']
            },
            {
              objection: `${input.competitor_info.name} has better market reputation/reviews`,
              response: 'While they do have strong brand recognition, if you look at recent reviews from the past 12 months, our customer satisfaction scores have overtaken theirs by 15 points, particularly in areas of support responsiveness and feature quality.',
              evidence: ['G2 Crowd comparison', 'Gartner Peer Insights trends']
            }
          ]
        },
        winning_strategies: {
          strategies: [
            {
              focus_area: 'Sales Cycle Positioning',
              strategy: 'Emphasize implementation speed and time-to-value',
              details: [
                'Highlight our 30-day implementation guarantee vs. their typical 90-day process',
                'Share case studies showing immediate ROI post-implementation',
                'Offer proof-of-concept in target environment'
              ],
              priority: 'High'
            },
            {
              focus_area: 'Technical Evaluation',
              strategy: 'Focus on user experience and simplicity',
              details: [
                'Push for hands-on evaluation by end users, not just technical team',
                'Demonstrate self-service capabilities not available in their platform',
                'Showcase our training completion rates (95%) vs. industry average (62%)'
              ],
              priority: 'Medium'
            },
            {
              focus_area: 'Pricing Discussions',
              strategy: 'Reframe value conversation to ROI not license cost',
              details: [
                'Present TCO calculator showing 3-year advantage',
                'Emphasize all-inclusive pricing vs. their module-based approach',
                'Demonstrate productivity gains that offset price difference'
              ],
              priority: 'High'
            }
          ]
        }
      },
      ai_generated: true,
      ai_model_used: 'Claude 3.7 Sonnet',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  },

  _mockFetchCompetitorUpdates: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return [
      { 
        id: 'update1', 
        competitor: 'Competitor A', 
        title: 'New Enterprise Plan Released', 
        description: 'Competitor A has launched a new Enterprise tier with advanced security features and dedicated support.',
        date: '2024-02-18',
        type: 'pricing',
        impact: 'medium' 
      },
      { 
        id: 'update2', 
        competitor: 'Competitor B', 
        title: 'European Market Expansion', 
        description: 'Competitor B announced opening new offices in Berlin and Paris as part of their European expansion strategy.',
        date: '2024-02-14',
        type: 'market',
        impact: 'high' 
      },
      { 
        id: 'update3', 
        competitor: 'Competitor C', 
        title: 'AI Integration Partnership', 
        description: 'Competitor C has partnered with an AI startup to enhance their analytics capabilities.',
        date: '2024-02-12',
        type: 'feature',
        impact: 'high' 
      }
    ];
  }
};

export default battlecardService;
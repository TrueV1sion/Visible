import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { toast } from 'react-toastify';

interface ApiConfig extends AxiosRequestConfig {
  retryConfig?: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
  };
}

interface ApiError {
  error_code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

class ApiClient {
  private client: AxiosInstance;
  private retryConfig: { maxRetries: number; baseDelay: number; maxDelay: number };
  private requestQueue: Map<string, Promise<any>> = new Map();

  constructor(config: ApiConfig = {}) {
    const { retryConfig, ...axiosConfig } = config;

    this.retryConfig = {
      maxRetries: retryConfig?.maxRetries || 3,
      baseDelay: retryConfig?.baseDelay || 1000,
      maxDelay: retryConfig?.maxDelay || 10000,
    };

    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
      ...axiosConfig,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId();

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor with retry logic
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const config = error.config as any;

        // Handle authentication errors
        if (error.response?.status === 401) {
          await this.handleAuthError();
          return Promise.reject(error);
        }

        // Handle rate limiting
        if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          const delay = retryAfter ? parseInt(retryAfter) * 1000 : 60000;
          
          toast.warning(`Rate limit exceeded. Retrying in ${delay / 1000} seconds...`);
          await this.sleep(delay);
          
          return this.client.request(config);
        }

        // Retry logic for retriable errors
        if (this.shouldRetry(error) && config && !config.__isRetryRequest) {
          return this.retryRequest(config);
        }

        // Handle and format other errors
        this.handleApiError(error);
        return Promise.reject(error);
      }
    );
  }

  private shouldRetry(error: AxiosError): boolean {
    // Retry on network errors or 5xx server errors
    if (!error.response) return true; // Network error
    
    const status = error.response.status;
    return status >= 500 && status < 600;
  }

  private async retryRequest(config: any): Promise<any> {
    config.__retryCount = config.__retryCount || 0;
    
    if (config.__retryCount >= this.retryConfig.maxRetries) {
      return Promise.reject(new Error('Max retries exceeded'));
    }

    config.__retryCount += 1;
    config.__isRetryRequest = true;

    // Calculate delay with exponential backoff and jitter
    const baseDelay = this.retryConfig.baseDelay * Math.pow(2, config.__retryCount - 1);
    const jitter = Math.random() * 0.1 * baseDelay;
    const delay = Math.min(baseDelay + jitter, this.retryConfig.maxDelay);

    await this.sleep(delay);
    return this.client.request(config);
  }

  private async handleAuthError(): Promise<void> {
    // Try to refresh token first
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      try {
        const response = await this.client.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken
        });
        
        const { access_token, refresh_token: newRefreshToken } = response.data;
        localStorage.setItem('authToken', access_token);
        localStorage.setItem('refreshToken', newRefreshToken);
        
        return;
      } catch (refreshError) {
        // Refresh failed, redirect to login
      }
    }
    
    // Clear invalid tokens and redirect
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    
    if (!window.location.pathname.includes('/login')) {
      toast.error('Session expired. Please sign in again.');
      window.location.href = '/login';
    }
  }

  private handleApiError(error: AxiosError): void {
    const apiError = this.extractApiError(error);
    
    // Show user-friendly error message
    const message = this.getErrorMessage(apiError);
    toast.error(message);

    // Log detailed error for debugging
    console.error('API Error:', {
      ...apiError,
      request: {
        url: error.config?.url,
        method: error.config?.method,
        data: error.config?.data,
      },
      response: {
        status: error.response?.status,
        data: error.response?.data,
      }
    });
  }

  private extractApiError(error: AxiosError): ApiError {
    if (error.response?.data && typeof error.response.data === 'object') {
      const data = error.response.data as any;
      return {
        error_code: data.error_code || `HTTP_${error.response.status}`,
        message: data.message || error.message,
        details: data.details || {},
        timestamp: data.timestamp || new Date().toISOString(),
      };
    }

    return {
      error_code: error.code || 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      details: {},
      timestamp: new Date().toISOString(),
    };
  }

  private getErrorMessage(error: ApiError): string {
    const messages: Record<string, string> = {
      VALIDATION_ERROR: 'Please check your input and try again',
      RESOURCE_NOT_FOUND: 'The requested item was not found',
      INSUFFICIENT_PERMISSIONS: 'You don\'t have permission to perform this action',
      AI_GENERATION_FAILED: 'AI content generation failed. Please try again',
      EXTERNAL_API_ERROR: 'External service is temporarily unavailable',
      RATE_LIMIT_EXCEEDED: 'Too many requests. Please wait before trying again',
      NETWORK_ERROR: 'Network error. Please check your connection',
    };

    return messages[error.error_code] || error.message || 'An unexpected error occurred';
  }

  private generateRequestId(): string {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Request deduplication
  private async dedupedRequest<T>(key: string, requestFn: () => Promise<T>): Promise<T> {
    if (this.requestQueue.has(key)) {
      return this.requestQueue.get(key)!;
    }

    const promise = requestFn().finally(() => {
      this.requestQueue.delete(key);
    });

    this.requestQueue.set(key, promise);
    return promise;
  }

  // Public API methods
  public async get<T>(
    url: string,
    config: AxiosRequestConfig = {}
  ): Promise<T> {
    const key = `GET:${url}:${JSON.stringify(config.params || {})}`;
    
    return this.dedupedRequest(key, async () => {
      const response: AxiosResponse<T> = await this.client.get(url, config);
      return response.data;
    });
  }

  public async post<T>(
    url: string,
    data?: any,
    config: AxiosRequestConfig = {}
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  public async put<T>(
    url: string,
    data?: any,
    config: AxiosRequestConfig = {}
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  public async delete<T>(
    url: string,
    config: AxiosRequestConfig = {}
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  public async upload<T>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<T> = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          onProgress(progress);
        }
      },
    });

    return response.data;
  }

  // Health check
  public async healthCheck(): Promise<{ status: string; timestamp: number }> {
    return this.get('/health');
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient();
export default ApiClient;
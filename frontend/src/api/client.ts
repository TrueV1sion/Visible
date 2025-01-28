import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { handleError, retryWithBackoff } from '../utils/errorHandling';

interface ApiClientConfig extends AxiosRequestConfig {
  retryConfig?: {
    maxRetries?: number;
    baseDelay?: number;
  };
}

class ApiClient {
  private client: AxiosInstance;
  private retryConfig: { maxRetries: number; baseDelay: number };

  constructor(config: ApiClientConfig = {}) {
    const { retryConfig, ...axiosConfig } = config;

    this.retryConfig = {
      maxRetries: retryConfig?.maxRetries || 3,
      baseDelay: retryConfig?.baseDelay || 1000,
    };

    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL,
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
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        // Handle token expiration
        if (error.response?.status === 401) {
          // Clear invalid token
          localStorage.removeItem('authToken');
          
          // Redirect to login if not already there
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private async request<T>(
    config: AxiosRequestConfig,
    context: Record<string, any> = {}
  ): Promise<T> {
    try {
      const operation = async () => {
        const response: AxiosResponse<T> = await this.client.request(config);
        return response.data;
      };

      return await retryWithBackoff(
        operation,
        this.retryConfig.maxRetries,
        this.retryConfig.baseDelay
      );
    } catch (error) {
      await handleError(error as Error, {
        context: {
          ...context,
          url: config.url,
          method: config.method,
        },
      });
      throw error;
    }
  }

  public async get<T>(
    url: string,
    config: AxiosRequestConfig = {},
    context: Record<string, any> = {}
  ): Promise<T> {
    return this.request<T>(
      {
        ...config,
        method: 'GET',
        url,
      },
      context
    );
  }

  public async post<T>(
    url: string,
    data?: any,
    config: AxiosRequestConfig = {},
    context: Record<string, any> = {}
  ): Promise<T> {
    return this.request<T>(
      {
        ...config,
        method: 'POST',
        url,
        data,
      },
      context
    );
  }

  public async put<T>(
    url: string,
    data?: any,
    config: AxiosRequestConfig = {},
    context: Record<string, any> = {}
  ): Promise<T> {
    return this.request<T>(
      {
        ...config,
        method: 'PUT',
        url,
        data,
      },
      context
    );
  }

  public async delete<T>(
    url: string,
    config: AxiosRequestConfig = {},
    context: Record<string, any> = {}
  ): Promise<T> {
    return this.request<T>(
      {
        ...config,
        method: 'DELETE',
        url,
      },
      context
    );
  }

  public async upload<T>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void,
    context: Record<string, any> = {}
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<T>(
      {
        method: 'POST',
        url,
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = (progressEvent.loaded / progressEvent.total) * 100;
            onProgress(progress);
          }
        },
      },
      {
        ...context,
        fileName: file.name,
        fileSize: file.size,
      }
    );
  }
}

// Create and export a singleton instance
export const api = new ApiClient();

// Export the class for testing or custom instances
export default ApiClient; 
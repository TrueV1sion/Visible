import { AxiosError } from 'axios';
import { toast } from 'react-toastify';

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface ErrorOptions {
  showToast?: boolean;
  logToServer?: boolean;
  context?: Record<string, any>;
}

const defaultOptions: ErrorOptions = {
  showToast: true,
  logToServer: true,
};

export const handleError = async (
  error: Error | AxiosError,
  options: ErrorOptions = defaultOptions
) => {
  const { showToast = true, logToServer = true, context = {} } = options;

  // Extract error details
  let errorDetails: ApiError = {
    code: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred',
    timestamp: new Date().toISOString(),
  };

  if (error instanceof AxiosError && error.response?.data) {
    const { code, message, details } = error.response.data;
    errorDetails = {
      code: code || `HTTP_${error.response.status}`,
      message: message || error.message,
      details: details || {},
      timestamp: new Date().toISOString(),
    };
  } else {
    errorDetails.message = error.message;
  }

  // Show toast notification if enabled
  if (showToast) {
    const toastMessage = getToastMessage(errorDetails);
    toast.error(toastMessage, {
      position: 'top-right',
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    });
  }

  // Log error to server if enabled
  if (logToServer) {
    await logErrorToServer(errorDetails, context);
  }

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error Details:', {
      ...errorDetails,
      context,
      originalError: error,
    });
  }

  return errorDetails;
};

const getToastMessage = (error: ApiError): string => {
  switch (error.code) {
    case 'UNAUTHORIZED':
      return 'Please sign in to continue';
    case 'FORBIDDEN':
      return 'You don\'t have permission to perform this action';
    case 'NOT_FOUND':
      return 'The requested resource was not found';
    case 'VALIDATION_ERROR':
      return 'Please check your input and try again';
    case 'RATE_LIMIT_EXCEEDED':
      return 'Too many requests. Please try again later';
    case 'AI_GENERATION_FAILED':
      return 'Failed to generate AI content. Please try again';
    case 'NETWORK_ERROR':
      return 'Network error. Please check your connection';
    default:
      return error.message || 'An unexpected error occurred';
  }
};

const logErrorToServer = async (
  error: ApiError,
  context: Record<string, any>
): Promise<void> => {
  try {
    const errorLog = {
      ...error,
      context,
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    // Send error to logging endpoint
    await fetch('/api/logs/error', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorLog),
    });
  } catch (loggingError) {
    // Fail silently in production, log in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Failed to log error:', loggingError);
    }
  }
};

export const createErrorBoundary = (
  component: string,
  operation: string
) => {
  return async <T>(
    promise: Promise<T>,
    options: ErrorOptions = defaultOptions
  ): Promise<T> => {
    try {
      return await promise;
    } catch (error) {
      await handleError(error as Error, {
        ...options,
        context: {
          ...options.context,
          component,
          operation,
        },
      });
      throw error;
    }
  };
};

// Utility function to check if an error is of a specific type
export const isErrorType = (error: ApiError, code: string): boolean => {
  return error.code === code;
};

// Utility function to extract validation errors
export const getValidationErrors = (error: ApiError): Record<string, string> => {
  if (error.code === 'VALIDATION_ERROR' && error.details) {
    return error.details as Record<string, string>;
  }
  return {};
};

// Retry utility with exponential backoff
export const retryWithBackoff = async <T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> => {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      
      // Don't retry on certain errors
      if (error instanceof AxiosError) {
        const status = error.response?.status;
        if (status === 401 || status === 403 || status === 404) {
          throw error;
        }
      }
      
      // Calculate delay with exponential backoff
      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
}; 
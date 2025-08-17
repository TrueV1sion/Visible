import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '../services/api';
import { toast } from 'react-toastify';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on app start
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Set up token refresh interval
  useEffect(() => {
    if (user) {
      const interval = setInterval(async () => {
        try {
          const tokenStatus = await authService.validateToken();
          if (!tokenStatus.valid) {
            await refreshAuth();
          }
        } catch (error) {
          console.error('Token validation failed:', error);
          await logout();
        }
      }, 5 * 60 * 1000); // Check every 5 minutes

      return () => clearInterval(interval);
    }
  }, [user]);

  const checkAuthStatus = async (): Promise<void> => {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      // Validate token and get user data
      const [tokenStatus, userData] = await Promise.all([
        authService.validateToken(),
        authService.getCurrentUser()
      ]);

      if (tokenStatus.valid) {
        setUser(userData);
      } else {
        // Try to refresh token
        await refreshAuth();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // Clear invalid tokens
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (
    email: string, 
    password: string
  ): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    
    try {
      const response = await authService.login(email, password);
      
      // Get user data after successful login
      const userData = await authService.getCurrentUser();
      setUser(userData);
      
      toast.success('Successfully signed in!');
      
      return { success: true };
      
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 
                          error.message || 
                          'Login failed. Please check your credentials.';
      
      toast.error(errorMessage);
      
      return { 
        success: false, 
        error: errorMessage 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      toast.info('You have been signed out');
    }
  };

  const refreshAuth = async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (!refreshToken) {
      await logout();
      return;
    }

    try {
      // Refresh tokens
      const response = await authService.refreshToken(refreshToken);
      
      // Get updated user data
      const userData = await authService.getCurrentUser();
      setUser(userData);
      
    } catch (error) {
      console.error('Token refresh failed:', error);
      await logout();
    }
  };

  const updateUser = (userData: Partial<User>): void => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshAuth,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// HOC for protected routes
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>,
  requiredRoles?: string[]
) => {
  return (props: P) => {
    const { user, isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
      return <div>Loading...</div>; // Replace with proper loading component
    }

    if (!isAuthenticated) {
      return <div>Please sign in to access this page</div>; // Replace with redirect
    }

    if (requiredRoles && user && !requiredRoles.includes(user.role)) {
      return <div>You don't have permission to access this page</div>;
    }

    return <Component {...props} />;
  };
};

// Hook for role-based access control
export const useRoleAccess = (requiredRoles: string | string[]): boolean => {
  const { user } = useAuth();
  
  if (!user) return false;
  
  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
  return roles.includes(user.role);
};
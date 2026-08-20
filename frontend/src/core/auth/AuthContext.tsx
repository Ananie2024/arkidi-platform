import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserProfile, UserRole } from '../types/auth.types';
import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (accessToken: string, refreshToken: string) => Promise<void>;
  logout: () => void;
  hasRole: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchUserProfile = async () => {
    try {
      const token = localStorage.getItem('arkidi_access_token');
      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }
      const res = await apiClient.get(API_ENDPOINTS.auth.me);
      if (res.data?.data) {
        setUser(res.data.data);
      }
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const login = async (accessToken: string, refreshToken: string) => {
    localStorage.setItem('arkidi_access_token', accessToken);
    localStorage.setItem('arkidi_refresh_token', refreshToken);
    await fetchUserProfile();
  };

  const logout = () => {
    localStorage.removeItem('arkidi_access_token');
    localStorage.removeItem('arkidi_refresh_token');
    setUser(null);
    window.location.href = '/login';
  };

  const hasRole = (roles: UserRole[]) => {
    if (!user) return false;
    if (user.role === 'SUPER_ADMIN') return true;
    return roles.includes(user.role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};

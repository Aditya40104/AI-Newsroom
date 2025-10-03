import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is logged in on app start
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await api.get('/api/auth/me');
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    try {
      setLoading(true);
      console.log('Attempting login with:', credentials);
      
      const response = await api.post('/api/auth/login', credentials);
      console.log('Login response:', response.data);
      
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.message || error.response?.data?.detail || 'Login failed. Please try again.' 
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      console.log('Attempting registration with:', userData);
      
      const response = await api.post('/api/auth/register', userData);
      console.log('Registration response:', response.data);
      
      const { access_token, user: newUser } = response.data;
      
      localStorage.setItem('token', access_token);
      setUser(newUser);
      
      return { success: true };
    } catch (error) {
      console.error('Registration failed:', error);
      return { 
        success: false, 
        error: error.message || error.response?.data?.detail || 'Registration failed. Please try again.' 
      };
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async (googleToken) => {
    try {
      const response = await api.post('/api/auth/oauth/google', {
        token: googleToken,
        provider: 'google'
      });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      console.error('Google login failed:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Google login failed'
      };
    }
  };

  const loginWithGitHub = async (githubToken) => {
    try {
      const response = await api.post('/api/auth/oauth/github', {
        token: githubToken,
        provider: 'github'
      });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      console.error('GitHub login failed:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'GitHub login failed'
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const hasRole = (requiredRole) => {
    if (!user) return false;
    
    const roleHierarchy = {
      'writer': 1,
      'editor': 2,
      'admin': 3
    };
    
    const userRoleLevel = roleHierarchy[user.role] || 0;
    const requiredRoleLevel = roleHierarchy[requiredRole] || 0;
    
    return userRoleLevel >= requiredRoleLevel;
  };

  const value = {
    user,
    login,
    register,
    loginWithGoogle,
    loginWithGitHub,
    logout,
    hasRole,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
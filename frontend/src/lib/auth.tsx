'use client';

/**
 * Authentication Context
 *
 * Manages authentication state across the application using React Context.
 * Features:
 * - Persistent login state via localStorage
 * - JWT token decoding to extract user info
 * - Auto-redirect on 401 errors (handled by apiClient)
 * - Login/register/logout/OAuth functions
 */

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost, apiGet } from './api';
import { User, OAuthProvider } from '@/types/user';
import { LoginRequest, RegisterRequest, TokenResponse, OAuthURLResponse, OAuthCallbackRequest } from '@/types/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  initiateOAuth: (provider: OAuthProvider) => Promise<void>;
  handleOAuthCallback: (provider: OAuthProvider, code: string, state?: string) => Promise<void>;
  setAuthFromToken: (tokenResponse: TokenResponse) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Decode JWT token to extract user information
 * Note: This is a simple base64 decode - validation happens on the backend
 */
function decodeToken(token: string): User | null {
  try {
    // JWT format: header.payload.signature
    const payload = token.split('.')[1];
    if (!payload) return null;

    // Base64 decode
    const decoded = JSON.parse(atob(payload));

    // Extract user_id from 'sub' claim
    const userId = decoded.sub;
    if (!userId) return null;

    // We only have user_id from JWT, email will be loaded separately if needed
    // For now, return a minimal user object
    return {
      id: userId,
      email: '', // Will be populated after login/register
    };
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Helper to store user in localStorage
  const storeUserData = useCallback((tokenResponse: TokenResponse) => {
    localStorage.setItem('jwt_token', tokenResponse.access_token);
    localStorage.setItem('user_id', tokenResponse.user.id);
    localStorage.setItem('user_email', tokenResponse.user.email);
    if (tokenResponse.user.name) {
      localStorage.setItem('user_name', tokenResponse.user.name);
    }
    if (tokenResponse.user.avatar_url) {
      localStorage.setItem('user_avatar', tokenResponse.user.avatar_url);
    }
    if (tokenResponse.user.oauth_provider) {
      localStorage.setItem('user_oauth_provider', tokenResponse.user.oauth_provider);
    }
  }, []);

  // On mount, check for existing token in localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('jwt_token');
    const storedUserId = localStorage.getItem('user_id');
    const storedUserEmail = localStorage.getItem('user_email');
    const storedUserName = localStorage.getItem('user_name');
    const storedUserAvatar = localStorage.getItem('user_avatar');
    const storedOAuthProvider = localStorage.getItem('user_oauth_provider');

    if (storedToken && storedUserId) {
      setToken(storedToken);
      setUser({
        id: storedUserId,
        email: storedUserEmail || '',
        name: storedUserName || null,
        avatar_url: storedUserAvatar || null,
        oauth_provider: storedOAuthProvider || null,
      });
    }

    setIsLoading(false);
  }, []);

  /**
   * Log in user with email and password
   */
  const login = async (email: string, password: string): Promise<void> => {
    try {
      const payload: LoginRequest = { email, password };
      const response = await apiPost<TokenResponse>('/api/auth/login', payload);

      // Store token and user info
      storeUserData(response);
      setToken(response.access_token);
      setUser(response.user);

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  /**
   * Register new user with email and password
   */
  const register = async (email: string, password: string): Promise<void> => {
    try {
      const payload: RegisterRequest = { email, password };
      const response = await apiPost<TokenResponse>('/api/auth/register', payload);

      // Store token and user info
      storeUserData(response);
      setToken(response.access_token);
      setUser(response.user);

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  /**
   * Log out user and clear authentication state
   */
  const logout = (): void => {
    // Clear localStorage
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_avatar');
    localStorage.removeItem('user_oauth_provider');

    // Clear state
    setToken(null);
    setUser(null);

    // Redirect to login page
    router.push('/');
  };

  /**
   * Initiate OAuth flow by redirecting to provider
   */
  const initiateOAuth = async (provider: OAuthProvider): Promise<void> => {
    try {
      const response = await apiGet<OAuthURLResponse>(`/api/auth/${provider}/url`);
      // Redirect to OAuth provider
      window.location.href = response.auth_url;
    } catch (error) {
      console.error(`Failed to initiate ${provider} OAuth:`, error);
      throw error;
    }
  };

  /**
   * Handle OAuth callback after user returns from provider
   */
  const handleOAuthCallback = async (
    provider: OAuthProvider,
    code: string,
    state?: string
  ): Promise<void> => {
    try {
      const payload: OAuthCallbackRequest = { code, state };
      const response = await apiPost<TokenResponse>(`/api/auth/${provider}/callback`, payload);

      // Store token and user info
      storeUserData(response);
      setToken(response.access_token);
      setUser(response.user);

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error(`${provider} OAuth callback failed:`, error);
      throw error;
    }
  };

  /**
   * Set auth state from token response (used by callback pages)
   */
  const setAuthFromToken = (tokenResponse: TokenResponse): void => {
    storeUserData(tokenResponse);
    setToken(tokenResponse.access_token);
    setUser(tokenResponse.user);
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
    initiateOAuth,
    handleOAuthCallback,
    setAuthFromToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access authentication context
 * Must be used within AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

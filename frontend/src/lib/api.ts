/**
 * API Client Module
 *
 * Handles all HTTP communication with the FastAPI backend.
 * Features:
 * - Automatic JWT token injection from localStorage
 * - 401 error handling with automatic redirect to login
 * - Type-safe request/response handling
 * - Centralized error handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiError extends Error {
  status?: number;
  data?: any;
}

/**
 * Main API client function for making authenticated requests to the backend.
 *
 * @param endpoint - API endpoint path (e.g., '/api/auth/login')
 * @param options - Fetch API options
 * @returns Parsed JSON response
 * @throws ApiError on non-2xx responses or network errors
 */
export async function apiClient<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Get JWT token from localStorage if available
  const token = typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null;

  // Build headers
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };

  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Construct full URL
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    // Make the request
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized - token expired or invalid
    if (response.status === 401) {
      // Clear invalid token
      if (typeof window !== 'undefined') {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user_id');

        // Redirect to login page
        window.location.href = '/';
      }

      const error = new Error('Authentication required') as ApiError;
      error.status = 401;
      throw error;
    }

    // Handle other non-2xx responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(
        errorData.detail || `Request failed with status ${response.status}`
      ) as ApiError;
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    // Parse and return JSON response
    // Handle 204 No Content responses
    if (response.status === 204) {
      return undefined as T;
    }

    return await response.json();
  } catch (error) {
    // Re-throw ApiError instances
    if ((error as ApiError).status) {
      throw error;
    }

    // Wrap network errors
    const apiError = new Error(
      `Network error: ${(error as Error).message}`
    ) as ApiError;
    throw apiError;
  }
}

/**
 * Helper function for GET requests
 */
export async function apiGet<T = any>(endpoint: string): Promise<T> {
  return apiClient<T>(endpoint, { method: 'GET' });
}

/**
 * Helper function for POST requests
 */
export async function apiPost<T = any>(
  endpoint: string,
  data?: any
): Promise<T> {
  return apiClient<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * Helper function for PUT requests
 */
export async function apiPut<T = any>(
  endpoint: string,
  data?: any
): Promise<T> {
  return apiClient<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * Helper function for DELETE requests
 */
export async function apiDelete<T = any>(endpoint: string): Promise<T> {
  return apiClient<T>(endpoint, { method: 'DELETE' });
}

/**
 * API Client Module
 *
 * Handles all HTTP communication with the FastAPI backend.
 * Uses NEXT_PUBLIC_API_BASE_URL environment variable.
 *
 * Production: https://tayyabaziz-todo-app-phase2.hf.space
 * Development: http://localhost:8000
 */

// Get API base URL from environment - NO localhost fallback in production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

// Validate API URL is set
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.error('[API] NEXT_PUBLIC_API_BASE_URL is not set!');
  console.error('[API] Set this in Vercel Environment Variables');
}

interface ApiError extends Error {
  status?: number;
  data?: unknown;
}

/**
 * Main API client function for making authenticated requests.
 */
export async function apiClient<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Get JWT token from localStorage
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

  // Log request in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`[API] ${options.method || 'GET'} ${url}`);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include', // Include cookies for CORS
    });

    // Log response status
    console.log(`[API] Response: ${response.status} ${response.statusText}`);

    // Handle 401 Unauthorized
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user_id');
        console.warn('[API] 401 Unauthorized - clearing tokens');
        window.location.href = '/login';
      }
      const error = new Error('Authentication required') as ApiError;
      error.status = 401;
      throw error;
    }

    // Handle other non-2xx responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`[API] Error ${response.status}:`, errorData);
      const error = new Error(
        errorData.detail || `Request failed with status ${response.status}`
      ) as ApiError;
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return await response.json();
  } catch (error) {
    // Log network errors
    console.error('[API] Request failed:', error);

    if ((error as ApiError).status) {
      throw error;
    }

    const apiError = new Error(
      `Network error: ${(error as Error).message}`
    ) as ApiError;
    throw apiError;
  }
}

/**
 * GET request helper
 */
export async function apiGet<T = unknown>(endpoint: string): Promise<T> {
  return apiClient<T>(endpoint, { method: 'GET' });
}

/**
 * POST request helper
 */
export async function apiPost<T = unknown>(
  endpoint: string,
  data?: unknown
): Promise<T> {
  return apiClient<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PUT request helper
 */
export async function apiPut<T = unknown>(
  endpoint: string,
  data?: unknown
): Promise<T> {
  return apiClient<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * DELETE request helper
 */
export async function apiDelete<T = unknown>(endpoint: string): Promise<T> {
  return apiClient<T>(endpoint, { method: 'DELETE' });
}

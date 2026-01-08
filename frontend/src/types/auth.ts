/**
 * Authentication type definitions
 *
 * Matches backend authentication schemas:
 * - RegisterRequest
 * - LoginRequest
 * - TokenResponse
 * - OAuth types
 */

import { User, OAuthProvider } from './user';

/**
 * Payload for user registration
 */
export interface RegisterRequest {
  email: string;
  password: string;
}

/**
 * Payload for user login
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Response from login or registration endpoints
 */
export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  user: User;
}

/**
 * Response containing OAuth authorization URL
 */
export interface OAuthURLResponse {
  auth_url: string;
  provider: OAuthProvider;
}

/**
 * Payload for OAuth callback
 */
export interface OAuthCallbackRequest {
  code: string;
  state?: string;
}

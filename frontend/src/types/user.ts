/**
 * User type definitions
 *
 * Matches backend User model and UserResponse schema
 */

export interface User {
  id: string; // UUID as string
  email: string;
  name?: string | null;
  avatar_url?: string | null;
  oauth_provider?: string | null;
}

export type OAuthProvider = 'google' | 'github';

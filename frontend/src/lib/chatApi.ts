/**
 * Chat API Client
 *
 * Handles communication with the backend chat API endpoint.
 * Uses NEXT_PUBLIC_API_BASE_URL environment variable.
 *
 * Note: Chat API is Phase 3 only - separate from Phase 2 backend.
 */

// Get API base URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

export interface ChatMessage {
  role: "user" | "assistant" | "tool";
  content: string;
  tool_calls?: Array<{
    tool: string;
    arguments: Record<string, unknown>;
    result: Record<string, unknown>;
  }>;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: Array<{
    tool: string;
    arguments: Record<string, unknown>;
    result: Record<string, unknown>;
  }>;
  finish_reason?: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  model?: string;
}

export interface SendMessageOptions {
  message: string;
  conversationId?: string;
  userId: string;
  authToken: string;
}

/**
 * Send a message to the chat API
 */
export async function sendMessage(options: SendMessageOptions): Promise<ChatResponse> {
  const { message, conversationId, userId, authToken } = options;

  const endpoint = `${API_BASE_URL}/api/${userId}/chat`;

  console.log(`[ChatAPI] POST ${endpoint}`);

  const requestBody: {
    message: string;
    conversation_id?: string;
  } = {
    message,
  };

  if (conversationId) {
    requestBody.conversation_id = conversationId;
  }

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${authToken}`,
      },
      body: JSON.stringify(requestBody),
      credentials: 'include',
    });

    console.log(`[ChatAPI] Response: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Authentication failed. Please log in again.");
      }
      if (response.status === 404) {
        throw new Error("Chat API not available. This feature requires Phase 3 backend.");
      }
      if (response.status === 500) {
        throw new Error("Server error. Please try again later.");
      }

      const errorText = await response.text();
      console.error(`[ChatAPI] Error: ${response.status}`, errorText);
      throw new Error(`API request failed: ${response.status} ${errorText}`);
    }

    const data: ChatResponse = await response.json();

    if (!data.message || !data.conversation_id) {
      throw new Error("Invalid response from chat API: missing required fields");
    }

    return data;
  } catch (error) {
    console.error('[ChatAPI] Request failed:', error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unexpected error occurred while sending the message");
  }
}

/**
 * Get user ID and auth token from localStorage
 */
export async function getUserAuth(): Promise<{ userId: string; authToken: string }> {
  if (typeof window === "undefined") {
    throw new Error("getUserAuth() must be called from browser environment");
  }

  const authToken = localStorage.getItem("jwt_token");
  const userId = localStorage.getItem("user_id");

  if (!authToken || !userId) {
    throw new Error("Not authenticated. Please log in to use the chat feature.");
  }

  return {
    userId,
    authToken,
  };
}

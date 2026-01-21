/**
 * Chat API Client
 *
 * Handles communication with the backend chat API endpoint.
 * Supports stateless conversation model using conversation_id.
 */

export interface ChatMessage {
  role: "user" | "assistant" | "tool";
  content: string;
  tool_calls?: Array<{
    tool: string;
    input: Record<string, unknown>;
    result: Record<string, unknown>;
  }>;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: Array<{
    tool: string;
    input: Record<string, unknown>;
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
 *
 * @param options - Message options including text, conversation ID, user ID, and auth token
 * @returns Chat response with assistant message and updated conversation ID
 */
export async function sendMessage(options: SendMessageOptions): Promise<ChatResponse> {
  const { message, conversationId, userId, authToken } = options;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const endpoint = `${apiUrl}/api/${userId}/chat`;

  const requestBody: {
    message: string;
    conversation_id?: string;
  } = {
    message,
  };

  // Include conversation_id if continuing an existing conversation
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
    });

    if (!response.ok) {
      // Handle HTTP errors
      if (response.status === 401) {
        throw new Error("Authentication failed. Please log in again.");
      }
      if (response.status === 404) {
        throw new Error("Chat API endpoint not found. Please check the backend URL.");
      }
      if (response.status === 500) {
        throw new Error("Server error. Please try again later.");
      }

      const errorText = await response.text();
      throw new Error(`API request failed: ${response.status} ${errorText}`);
    }

    const data: ChatResponse = await response.json();

    // Validate response structure
    if (!data.message || !data.conversation_id) {
      throw new Error("Invalid response from chat API: missing required fields");
    }

    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unexpected error occurred while sending the message");
  }
}

/**
 * Get user ID and auth token from Better Auth session
 *
 * This is a placeholder - implement based on your Better Auth integration
 *
 * @returns User ID and auth token
 */
export async function getUserAuth(): Promise<{ userId: string; authToken: string }> {
  // TODO: Implement Better Auth integration
  // For now, return placeholder values
  // In production, extract from Better Auth session cookie or context

  // Example implementation (adjust based on your Better Auth setup):
  // const session = await auth.getSession();
  // if (!session || !session.user) {
  //   throw new Error("Not authenticated");
  // }
  // return {
  //   userId: session.user.id,
  //   authToken: session.accessToken,
  // };

  throw new Error("Authentication not implemented. Please implement getUserAuth() with Better Auth integration.");
}

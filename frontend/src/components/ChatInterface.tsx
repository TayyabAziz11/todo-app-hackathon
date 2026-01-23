"use client";

/**
 * ChatInterface Component
 *
 * Integrates OpenAI ChatKit with the backend chat API.
 * Supports:
 * - Stateless conversation model (conversation_id stored in sessionStorage)
 * - JWT authentication
 * - Tool call transparency (displays which MCP tools were invoked)
 * - Loading states and error handling
 */

import { useState, useEffect, useCallback } from "react";
import { sendMessage, getUserAuth, ChatResponse } from "@/lib/chatApi";

// Storage key for conversation ID persistence
const CONVERSATION_ID_KEY = "todo_chat_conversation_id";

export default function ChatInterface() {
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [toolCalls, setToolCalls] = useState<Array<{
    tool: string;
    input: Record<string, unknown>;
    result: Record<string, unknown>;
  }>>([]);

  // Load conversation ID from sessionStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedConversationId = sessionStorage.getItem(CONVERSATION_ID_KEY);
      if (storedConversationId) {
        setConversationId(storedConversationId);
        console.log("Loaded conversation ID from storage:", storedConversationId);
      }
    }
  }, []);

  // Initialize authentication
  useEffect(() => {
    async function initAuth() {
      try {
        const auth = await getUserAuth();
        setUserId(auth.userId);
        setAuthToken(auth.authToken);
        setAuthError(null);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Authentication failed";
        setAuthError(errorMessage);
        console.error("Authentication error:", error);
      }
    }

    initAuth();
  }, []);

  // Save conversation ID to sessionStorage whenever it changes
  useEffect(() => {
    if (conversationId && typeof window !== "undefined") {
      sessionStorage.setItem(CONVERSATION_ID_KEY, conversationId);
      console.log("Saved conversation ID to storage:", conversationId);
    }
  }, [conversationId]);

  /**
   * Handle sending a message to the backend
   */
  const handleSendMessage = useCallback(async (userMessage: string) => {
    if (!userId || !authToken) {
      setError("Not authenticated. Please log in.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setToolCalls([]);

    // Add user message to UI immediately
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    try {
      // Call backend API
      const response: ChatResponse = await sendMessage({
        message: userMessage,
        conversationId,
        userId,
        authToken,
      });

      // Update conversation ID
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to UI
      setMessages((prev) => [...prev, { role: "assistant", content: response.message }]);

      // Display tool calls if any
      if (response.tool_calls && response.tool_calls.length > 0) {
        setToolCalls(response.tool_calls);
        console.log("Tool calls executed:", response.tool_calls);
      }

      // Log usage stats if available
      if (response.usage) {
        console.log("Token usage:", response.usage);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to send message";
      setError(errorMessage);
      console.error("Send message error:", error);

      // Remove the user message from UI if send failed
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, userId, authToken]);

  /**
   * Clear conversation and start fresh
   */
  const handleClearConversation = useCallback(() => {
    setConversationId(undefined);
    setMessages([]);
    setToolCalls([]);
    setError(null);
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(CONVERSATION_ID_KEY);
    }
    console.log("Conversation cleared");
  }, []);

  // Show authentication error if not authenticated
  if (authError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
        <div className="bg-white rounded-lg shadow-md p-6 max-w-md w-full">
          <div className="flex items-center text-red-600 mb-4">
            <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-lg font-semibold">Authentication Required</h2>
          </div>
          <p className="text-gray-700 mb-4">{authError}</p>
          <p className="text-sm text-gray-500">
            Please implement Better Auth integration in <code className="bg-gray-100 px-1 rounded">src/lib/chatApi.ts</code>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Todo AI Chatbot</h1>
            <div className="flex items-center gap-3 mt-1">
              <p className="text-sm text-gray-500">
                {conversationId ? `Conversation: ${conversationId.substring(0, 8)}...` : "New conversation"}
              </p>
              {conversationId && (
                <span className="inline-flex items-center gap-1 text-xs text-green-600">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Saved automatically
                </span>
              )}
            </div>
          </div>
          <button
            onClick={handleClearConversation}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Clear Chat
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <p className="text-lg font-medium">Start a conversation</p>
              <p className="text-sm mt-2">Try: &quot;Add a task to buy groceries&quot; or &quot;Show my tasks&quot;</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-3xl rounded-lg p-4 ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-white border border-gray-200 text-gray-900"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))
          )}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tool Call Transparency */}
      {toolCalls.length > 0 && (
        <div className="bg-blue-50 border-t border-blue-200 p-3">
          <div className="max-w-4xl mx-auto">
            <p className="text-sm font-medium text-blue-900 mb-2">🔧 Tools Used:</p>
            <div className="flex flex-wrap gap-2">
              {toolCalls.map((call, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {call.tool}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-t border-red-200 p-3">
          <div className="max-w-4xl mx-auto flex items-center text-red-800">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const form = e.currentTarget;
              const input = form.elements.namedItem("message") as HTMLInputElement;
              if (input.value.trim()) {
                handleSendMessage(input.value.trim());
                input.value = "";
              }
            }}
            className="flex space-x-4"
          >
            <input
              type="text"
              name="message"
              placeholder="Type your message... (e.g., 'Add a task to buy groceries')"
              disabled={isLoading}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? "Sending..." : "Send"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

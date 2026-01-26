"use client";

/**
 * Professional ChatInterface Component
 *
 * Features:
 * - Fixed input at bottom (no scrolling needed to type)
 * - Auto-scroll to latest message
 * - Conversation history sidebar
 * - Modern ChatGPT-style design
 * - Loading indicators
 * - Tool call transparency
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { sendMessage, getUserAuth, ChatResponse } from "@/lib/chatApi";
import ConversationSidebar from "./chat/ConversationSidebar";
import MessageBubble from "./chat/MessageBubble";
import ChatInput from "./chat/ChatInput";

// Storage keys
const CONVERSATION_ID_KEY = "todo_chat_conversation_id";
const CONVERSATIONS_HISTORY_KEY = "todo_chat_conversations";

export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

export interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  updatedAt: number;
  messages: Message[];
}

export default function ChatInterface() {
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  // Load conversation history from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedConversationId = sessionStorage.getItem(CONVERSATION_ID_KEY);
      const storedConversations = localStorage.getItem(CONVERSATIONS_HISTORY_KEY);

      if (storedConversationId) {
        setConversationId(storedConversationId);
      }

      if (storedConversations) {
        try {
          setConversations(JSON.parse(storedConversations));
        } catch (e) {
          console.error("Failed to parse conversations:", e);
        }
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

  // Save conversation to history
  const saveConversationToHistory = useCallback((convId: string, msgs: Message[]) => {
    if (typeof window === "undefined" || msgs.length === 0) return;

    const lastMessage = msgs[msgs.length - 1];
    const title = msgs.find(m => m.role === "user")?.content.substring(0, 50) || "New conversation";

    const conversation: Conversation = {
      id: convId,
      title,
      lastMessage: lastMessage.content.substring(0, 60) + (lastMessage.content.length > 60 ? "..." : ""),
      updatedAt: Date.now(),
      messages: msgs,
    };

    setConversations(prev => {
      const filtered = prev.filter(c => c.id !== convId);
      const updated = [conversation, ...filtered].slice(0, 20); // Keep last 20 conversations
      localStorage.setItem(CONVERSATIONS_HISTORY_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  // Load a conversation from history
  const loadConversation = useCallback((conversation: Conversation) => {
    setConversationId(conversation.id);
    setMessages(conversation.messages);
    sessionStorage.setItem(CONVERSATION_ID_KEY, conversation.id);
  }, []);

  // Handle sending a message
  const handleSendMessage = useCallback(async (userMessage: string) => {
    if (!userId || !authToken) {
      setError("Not authenticated. Please log in.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const newUserMessage: Message = {
      role: "user",
      content: userMessage,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response: ChatResponse = await sendMessage({
        message: userMessage,
        conversationId,
        userId,
        authToken,
      });

      const newAssistantMessage: Message = {
        role: "assistant",
        content: response.message,
        timestamp: Date.now(),
      };

      setMessages(prev => {
        const updated = [...prev, newAssistantMessage];
        saveConversationToHistory(response.conversation_id, updated);
        return updated;
      });

      if (response.conversation_id && response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id);
        sessionStorage.setItem(CONVERSATION_ID_KEY, response.conversation_id);
      }

      if (response.tool_calls && response.tool_calls.length > 0) {
        console.log("Tool calls executed:", response.tool_calls);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to send message";
      setError(errorMessage);
      console.error("Send message error:", error);
      setMessages(prev => prev.slice(0, -1)); // Remove failed user message
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, userId, authToken, saveConversationToHistory]);

  // Start a new conversation
  const handleNewConversation = useCallback(() => {
    setConversationId(undefined);
    setMessages([]);
    setError(null);
    sessionStorage.removeItem(CONVERSATION_ID_KEY);
  }, []);

  // Delete a conversation
  const handleDeleteConversation = useCallback((convId: string) => {
    setConversations(prev => {
      const updated = prev.filter(c => c.id !== convId);
      localStorage.setItem(CONVERSATIONS_HISTORY_KEY, JSON.stringify(updated));
      return updated;
    });

    if (convId === conversationId) {
      handleNewConversation();
    }
  }, [conversationId, handleNewConversation]);

  // Show authentication error
  if (authError) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <div className="flex items-center text-red-600 mb-4">
            <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-lg font-semibold">Authentication Required</h2>
          </div>
          <p className="text-gray-700 mb-4">{authError}</p>
          <a href="/login" className="text-blue-600 hover:underline text-sm">
            Go to Login →
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <ConversationSidebar
        conversations={conversations}
        currentConversationId={conversationId}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onNewConversation={handleNewConversation}
        onLoadConversation={loadConversation}
        onDeleteConversation={handleDeleteConversation}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Todo AI Assistant</h1>
                <p className="text-sm text-gray-500">
                  {conversationId ? "Conversation active" : "New conversation"}
                </p>
              </div>
            </div>
            <button
              onClick={handleNewConversation}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
          </div>
        </div>

        {/* Messages Area - Scrollable */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Start a conversation</h3>
                <p className="text-sm text-gray-500 mb-6">
                  Ask me to manage your tasks, or just chat!
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  <button
                    onClick={() => handleSendMessage("Add a task to buy groceries")}
                    className="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Add a task to buy groceries
                  </button>
                  <button
                    onClick={() => handleSendMessage("Show me all my tasks")}
                    className="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Show me all my tasks
                  </button>
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, index) => (
                  <MessageBubble key={index} message={msg} />
                ))}
                {isLoading && (
                  <MessageBubble
                    message={{ role: "assistant", content: "", timestamp: Date.now() }}
                    isLoading
                  />
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-t border-red-200 px-6 py-3">
            <div className="max-w-3xl mx-auto flex items-center text-red-800">
              <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 hover:text-red-800"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Input Area - Fixed at Bottom */}
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder="Type your message... Try 'Add a task' or 'Show my tasks'"
        />
      </div>
    </div>
  );
}

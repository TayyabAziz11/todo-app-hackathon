# Skill: integrate-chatkit-ui

**Version**: 1.0.0
**Created**: 2026-01-19
**Category**: Phase 3 - Frontend Layer

---

## 1. Purpose

Implement the ChatKit-based UI for Phase 3 AI Chatbot, connecting the Next.js frontend to the backend chat API endpoint. This skill covers ChatKit configuration, conversation_id persistence, backend API integration, tool call rendering, and user experience patterns.

All AI logic remains in the backend - the frontend is a pure presentation layer that sends messages and displays responses.

---

## 2. Applicable Agents

**Primary Agent**: `chatkit-frontend-integrator`
- Integrates OpenAI ChatKit with backend API
- Implements conversation persistence on client side
- Configures domain allowlist
- Handles frontend-to-backend communication

**Supporting Agents**:
- `nextjs-frontend-architect` - UI architecture review
- `chat-api-orchestrator` - API contract alignment

---

## 3. Input

### Prerequisites
- Backend chat endpoint: `POST /api/{user_id}/chat`
- Authentication system with JWT tokens
- Next.js 15+ with App Router
- User authentication state available

### Requirements
- ChatKit UI component integration
- Conversation ID persistence (localStorage/sessionStorage)
- Backend API connectivity
- Tool call transparency (show which tools were used)
- Error handling and loading states
- No AI logic in frontend (all reasoning in backend)

---

## 4. Output

### ChatKit Installation

**Install ChatKit package**:

```bash
cd frontend
npm install @openai/chatkit
```

**Package.json update**:
```json
{
  "dependencies": {
    "@openai/chatkit": "^1.0.0",
    "next": "^15.1.3",
    "react": "^19.0.0"
  }
}
```

---

### Environment Configuration

**File**: `frontend/.env.local`

```bash
# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-from-openai-console

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production (Vercel)
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**File**: `frontend/.env.example`

```bash
# OpenAI ChatKit Domain Key
# Get this from: https://platform.openai.com/settings/organization/chat-kit
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### Chat Page Component

**File**: `frontend/app/chat/page.tsx`

```tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ChatKit } from '@openai/chatkit';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: Array<{
    tool_name: string;
    arguments: Record<string, any>;
    result: any;
  }>;
}

export default function ChatPage() {
  const router = useRouter();
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Load authentication state
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('user_id');

    if (!token || !user) {
      // Redirect to login if not authenticated
      router.push('/login');
      return;
    }

    setAuthToken(token);
    setUserId(user);

    // Load existing conversation_id if resuming
    const savedConvId = sessionStorage.getItem('conversation_id');
    if (savedConvId) {
      setConversationId(savedConvId);
    }
  }, [router]);

  /**
   * Send message to backend chat API.
   *
   * Flow:
   * 1. Send user message + optional conversation_id to backend
   * 2. Backend runs AI agent with MCP tools
   * 3. Backend returns assistant response + conversation_id
   * 4. Save conversation_id for future messages
   * 5. Return assistant message to ChatKit for display
   */
  const handleSendMessage = async (message: string): Promise<string> => {
    if (!userId || !authToken) {
      throw new Error('Not authenticated');
    }

    setIsLoading(true);
    setError(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/${userId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired - redirect to login
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_id');
          router.push('/login');
          throw new Error('Session expired');
        }

        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();

      // Save conversation_id for future messages
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
        sessionStorage.setItem('conversation_id', data.conversation_id);
      }

      // Log tool calls for debugging
      if (data.tool_calls && data.tool_calls.length > 0) {
        console.log('Tools used:', data.tool_calls.map((tc: any) => tc.tool_name));
      }

      return data.message;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;

    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Start a new conversation.
   */
  const handleNewConversation = () => {
    setConversationId(null);
    sessionStorage.removeItem('conversation_id');
  };

  // Show loading state while checking auth
  if (!userId || !authToken) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            Todo AI Assistant
          </h1>
          <div className="flex gap-4">
            {conversationId && (
              <button
                onClick={handleNewConversation}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                New Conversation
              </button>
            )}
            <button
              onClick={() => {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_id');
                router.push('/login');
              }}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Chat Container */}
      <main className="flex-1 overflow-hidden">
        <ChatKit
          onSendMessage={handleSendMessage}
          placeholder="Ask me to manage your tasks..."
          className="h-full"
          disabled={isLoading}
          domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
        />
      </main>

      {/* Status Bar */}
      <footer className="bg-white border-t border-gray-200 px-6 py-2">
        <div className="flex justify-between items-center text-sm text-gray-500">
          <span>
            {conversationId
              ? `Conversation: ${conversationId.slice(0, 8)}...`
              : 'New conversation'}
          </span>
          {isLoading && (
            <span className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
              AI is thinking...
            </span>
          )}
        </div>
      </footer>
    </div>
  );
}
```

---

### Enhanced Chat with Tool Display

**File**: `frontend/app/chat-enhanced/page.tsx`

```tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface ToolCall {
  tool_name: string;
  arguments: Record<string, any>;
  result: any;
  success: boolean;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCall[];
  timestamp: Date;
}

export default function EnhancedChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('user_id');

    if (!token || !user) {
      router.push('/login');
      return;
    }

    setAuthToken(token);
    setUserId(user);

    const savedConvId = sessionStorage.getItem('conversation_id');
    if (savedConvId) {
      setConversationId(savedConvId);
      // TODO: Load conversation history from backend
    }
  }, [router]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !userId || !authToken || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/${userId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      // Save conversation_id
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
        sessionStorage.setItem('conversation_id', data.conversation_id);
      }

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        tool_calls: data.tool_calls,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      // Add error message
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm px-6 py-4 border-b">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Todo AI Assistant</h1>
          <button
            onClick={() => {
              setMessages([]);
              setConversationId(null);
              sessionStorage.removeItem('conversation_id');
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            New Chat
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <p className="text-xl mb-2">👋 Welcome!</p>
            <p>I can help you manage your tasks. Try:</p>
            <ul className="mt-4 space-y-2">
              <li>"Show me all my tasks"</li>
              <li>"Add a task to buy groceries"</li>
              <li>"Mark task 1 as complete"</li>
            </ul>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-900 shadow'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>

              {/* Tool Calls Display */}
              {msg.tool_calls && msg.tool_calls.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500 mb-2">Tools used:</p>
                  <div className="space-y-1">
                    {msg.tool_calls.map((tool, idx) => (
                      <div
                        key={idx}
                        className="text-xs bg-gray-50 rounded px-2 py-1 flex items-center gap-2"
                      >
                        <span className={tool.success ? 'text-green-600' : 'text-red-600'}>
                          {tool.success ? '✓' : '✗'}
                        </span>
                        <span className="font-mono">{tool.tool_name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <p className="text-xs mt-2 opacity-70">
                {msg.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-lg px-4 py-3 shadow">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
                <span className="text-gray-600">Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600 resize-none"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

### API Client Utility

**File**: `frontend/lib/chat-api.ts`

```typescript
/**
 * Chat API client for backend communication.
 *
 * Handles authentication, error handling, and response parsing.
 */

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  tool_calls: Array<{
    tool_name: string;
    arguments: Record<string, any>;
    result: any;
    success: boolean;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export class ChatAPIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ChatAPIError';
  }
}

/**
 * Send a chat message to the backend.
 */
export async function sendChatMessage(
  userId: string,
  request: ChatRequest,
  authToken: string
): Promise<ChatResponse> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${apiUrl}/api/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ChatAPIError(
      errorData.detail || 'Failed to send message',
      response.status,
      errorData.detail
    );
  }

  return response.json();
}

/**
 * Get conversation history (future enhancement).
 */
export async function getConversationHistory(
  userId: string,
  conversationId: string,
  authToken: string
): Promise<any[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(
    `${apiUrl}/api/${userId}/conversations/${conversationId}/messages`,
    {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    }
  );

  if (!response.ok) {
    throw new ChatAPIError('Failed to fetch history', response.status);
  }

  return response.json();
}

/**
 * List user's conversations (future enhancement).
 */
export async function listConversations(
  userId: string,
  authToken: string
): Promise<any[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${apiUrl}/api/${userId}/conversations`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
    },
  });

  if (!response.ok) {
    throw new ChatAPIError('Failed to fetch conversations', response.status);
  }

  return response.json();
}
```

---

### Conversation ID Hook

**File**: `frontend/hooks/useConversation.ts`

```typescript
import { useState, useEffect } from 'react';

/**
 * Hook for managing conversation ID persistence.
 *
 * Stores conversation_id in sessionStorage so it persists
 * across page refreshes but not across browser sessions.
 */
export function useConversation() {
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Load from sessionStorage on mount
  useEffect(() => {
    const saved = sessionStorage.getItem('conversation_id');
    if (saved) {
      setConversationId(saved);
    }
  }, []);

  // Save to sessionStorage when updated
  const updateConversationId = (id: string | null) => {
    setConversationId(id);
    if (id) {
      sessionStorage.setItem('conversation_id', id);
    } else {
      sessionStorage.removeItem('conversation_id');
    }
  };

  // Start new conversation
  const startNewConversation = () => {
    updateConversationId(null);
  };

  return {
    conversationId,
    setConversationId: updateConversationId,
    startNewConversation,
  };
}
```

---

### TypeScript Types

**File**: `frontend/types/chat.ts`

```typescript
export interface ToolCall {
  tool_call_id: string;
  tool_name: string;
  arguments: Record<string, any>;
  result: any;
  success: boolean;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'tool';
  content: string;
  tool_calls?: ToolCall[];
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  tool_calls: ToolCall[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}
```

---

## 5. Key Features

### Conversation ID Persistence

**sessionStorage Pattern**:
```typescript
// Save when received from backend
sessionStorage.setItem('conversation_id', data.conversation_id);

// Load on page mount
const savedConvId = sessionStorage.getItem('conversation_id');

// Clear for new conversation
sessionStorage.removeItem('conversation_id');
```

**Why sessionStorage**:
- Persists across page refreshes
- Cleared when browser tab closed
- Separate conversations per tab

---

### Tool Call Transparency

**Display which tools were used**:
```tsx
{message.tool_calls && message.tool_calls.length > 0 && (
  <div className="tool-calls">
    <p>Tools used:</p>
    {message.tool_calls.map(tool => (
      <span key={tool.tool_name}>
        {tool.success ? '✓' : '✗'} {tool.tool_name}
      </span>
    ))}
  </div>
)}
```

**Benefits**:
- Users see what actions were taken
- Builds trust in AI system
- Debugging aid

---

### No AI Logic in Frontend

**Frontend responsibilities**:
- ✅ Capture user input
- ✅ Send to backend API
- ✅ Display response
- ✅ Handle errors
- ✅ Manage UI state

**Backend responsibilities**:
- ✅ Intent classification
- ✅ Tool selection
- ✅ Tool execution
- ✅ Response generation
- ✅ Conversation history

---

### Error Handling

```typescript
try {
  const response = await sendChatMessage(userId, request, token);
  // Handle success
} catch (error) {
  if (error instanceof ChatAPIError) {
    if (error.statusCode === 401) {
      // Redirect to login
      router.push('/login');
    } else if (error.statusCode === 404) {
      // Conversation not found
      setError('Conversation not found');
    } else {
      // Generic error
      setError(error.message);
    }
  }
}
```

---

## 6. Domain Allowlist Configuration

### Get Domain Key

1. Go to: https://platform.openai.com/settings/organization/chat-kit
2. Create new domain key
3. Add allowed domains:
   - `http://localhost:3000` (development)
   - `https://your-app.vercel.app` (production)

### Configure in Code

```tsx
<ChatKit
  domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
  // ... other props
/>
```

### Vercel Environment Variables

```bash
# In Vercel dashboard or CLI
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY
# Enter value: your_domain_key_here

vercel env add NEXT_PUBLIC_API_URL
# Enter value: https://your-backend.railway.app
```

---

## 7. Deployment Configuration

### Next.js Config

**File**: `frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable API proxy for development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL + '/api/:path*',
      },
    ];
  },

  // Environment variable validation
  env: {
    NEXT_PUBLIC_OPENAI_DOMAIN_KEY: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

module.exports = nextConfig;
```

---

### CORS Configuration (Backend)

**File**: `backend/app/main.py` (update)

```python
from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # Local development
        "https://your-app.vercel.app",    # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 8. Testing Strategy

### Manual Testing Checklist

- [ ] Send first message (creates new conversation)
- [ ] Verify conversation_id saved in sessionStorage
- [ ] Send second message (continues conversation)
- [ ] Verify conversation_id included in request
- [ ] Refresh page and send message (resumes conversation)
- [ ] Click "New Conversation" button (clears conversation_id)
- [ ] Test tool call display (add task, list tasks)
- [ ] Test error handling (invalid token, network error)
- [ ] Test loading states (spinner while waiting)
- [ ] Test logout and login flow

---

### Unit Tests

**File**: `frontend/__tests__/useConversation.test.ts`

```typescript
import { renderHook, act } from '@testing-library/react';
import { useConversation } from '@/hooks/useConversation';

describe('useConversation', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it('should start with null conversation_id', () => {
    const { result } = renderHook(() => useConversation());
    expect(result.current.conversationId).toBeNull();
  });

  it('should load conversation_id from sessionStorage', () => {
    sessionStorage.setItem('conversation_id', 'test-id');
    const { result } = renderHook(() => useConversation());
    expect(result.current.conversationId).toBe('test-id');
  });

  it('should save conversation_id to sessionStorage', () => {
    const { result } = renderHook(() => useConversation());

    act(() => {
      result.current.setConversationId('new-id');
    });

    expect(result.current.conversationId).toBe('new-id');
    expect(sessionStorage.getItem('conversation_id')).toBe('new-id');
  });

  it('should clear conversation_id', () => {
    sessionStorage.setItem('conversation_id', 'test-id');
    const { result } = renderHook(() => useConversation());

    act(() => {
      result.current.startNewConversation();
    });

    expect(result.current.conversationId).toBeNull();
    expect(sessionStorage.getItem('conversation_id')).toBeNull();
  });
});
```

---

## 9. Common Issues and Solutions

### Issue: ChatKit not displaying

**Problem**: White screen or ChatKit doesn't render

**Solution**:
```typescript
// Ensure domainKey is set
console.log('Domain key:', process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY);

// Check ChatKit is imported correctly
import { ChatKit } from '@openai/chatkit';

// Verify environment variables loaded
if (!process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY) {
  console.error('Missing NEXT_PUBLIC_OPENAI_DOMAIN_KEY');
}
```

---

### Issue: CORS errors

**Problem**: Browser console shows CORS policy errors

**Solution**:
```python
# Backend: Add frontend URL to CORS origins
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend.vercel.app",
]
```

---

### Issue: Conversation not resuming

**Problem**: New messages start fresh conversation

**Solution**:
```typescript
// Ensure conversation_id included in request
const response = await fetch(`/api/${userId}/chat`, {
  body: JSON.stringify({
    message: userMessage,
    conversation_id: conversationId,  // Must include this!
  }),
});
```

---

### Issue: Tool calls not showing

**Problem**: Backend returns tool_calls but not displayed

**Solution**:
```tsx
// Check tool_calls structure matches expected format
console.log('Tool calls:', data.tool_calls);

// Ensure conditional rendering correct
{message.tool_calls && Array.isArray(message.tool_calls) && (
  <div>...</div>
)}
```

---

## 10. Future Enhancements

### Conversation List Sidebar

```tsx
<aside className="w-64 bg-white border-r">
  <h2>Conversations</h2>
  {conversations.map(conv => (
    <button
      key={conv.id}
      onClick={() => setConversationId(conv.id)}
      className={conversationId === conv.id ? 'active' : ''}
    >
      {conv.title}
    </button>
  ))}
</aside>
```

---

### Streaming Responses

```typescript
// Use Server-Sent Events for real-time streaming
const response = await fetch(`/api/${userId}/chat/stream`, {
  // ... config
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // Update UI with partial response
}
```

---

### Voice Input

```tsx
import { useSpeechRecognition } from 'react-speech-recognition';

const { transcript, listening, startListening } = useSpeechRecognition();

<button onClick={startListening}>
  {listening ? '🎤 Listening...' : '🎤 Voice Input'}
</button>
```

---

## Implementation Checklist

- [ ] Install ChatKit package: `npm install @openai/chatkit`
- [ ] Create `.env.local` with NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- [ ] Get domain key from OpenAI console
- [ ] Create chat page component (`app/chat/page.tsx`)
- [ ] Implement handleSendMessage function
- [ ] Add conversation_id persistence (sessionStorage)
- [ ] Create API client utility (`lib/chat-api.ts`)
- [ ] Create useConversation hook
- [ ] Add TypeScript types
- [ ] Configure CORS on backend
- [ ] Add authentication check and redirect
- [ ] Implement error handling and loading states
- [ ] Add tool call display in UI
- [ ] Add "New Conversation" button
- [ ] Test conversation resume across page refreshes
- [ ] Test tool call transparency
- [ ] Deploy to Vercel with environment variables
- [ ] Verify domain allowlist configuration
- [ ] Test production deployment end-to-end

---

**Skill Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: Ready for Implementation

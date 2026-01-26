"use client";

/**
 * MessageBubble Component
 *
 * Displays a single message in ChatGPT-style bubble
 */

import { Message } from "../ChatInterface";

interface MessageBubbleProps {
  message: Message;
  isLoading?: boolean;
}

export default function MessageBubble({ message, isLoading }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className="flex gap-3 max-w-[80%]">
        {/* Avatar */}
        {!isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white text-sm font-semibold">
            AI
          </div>
        )}

        {/* Message Content */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-white border border-gray-200 text-gray-900 shadow-sm"
          }`}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2 py-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
            </div>
          ) : (
            <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
              {message.content}
            </p>
          )}
        </div>

        {/* User Avatar */}
        {isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center text-white text-sm font-semibold">
            U
          </div>
        )}
      </div>
    </div>
  );
}

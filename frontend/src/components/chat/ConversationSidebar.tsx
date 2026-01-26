"use client";

/**
 * ConversationSidebar Component
 *
 * Displays conversation history with search and management
 */

import { Conversation } from "../ChatInterface";

interface ConversationSidebarProps {
  conversations: Conversation[];
  currentConversationId?: string;
  isOpen: boolean;
  onToggle: () => void;
  onNewConversation: () => void;
  onLoadConversation: (conversation: Conversation) => void;
  onDeleteConversation: (conversationId: string) => void;
}

export default function ConversationSidebar({
  conversations,
  currentConversationId,
  isOpen,
  onToggle,
  onNewConversation,
  onLoadConversation,
  onDeleteConversation,
}: ConversationSidebarProps) {
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const groupConversationsByDate = () => {
    const groups: { [key: string]: Conversation[] } = {
      Today: [],
      Yesterday: [],
      "This Week": [],
      Older: [],
    };

    conversations.forEach((conv) => {
      const diffDays = Math.floor((Date.now() - conv.updatedAt) / (1000 * 60 * 60 * 24));
      if (diffDays === 0) groups.Today.push(conv);
      else if (diffDays === 1) groups.Yesterday.push(conv);
      else if (diffDays < 7) groups["This Week"].push(conv);
      else groups.Older.push(conv);
    });

    return Object.entries(groups).filter(([_, convs]) => convs.length > 0);
  };

  return (
    <>
      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div
        className={`${
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        } fixed lg:static inset-y-0 left-0 z-50 w-80 bg-white border-r border-gray-200 flex flex-col transition-transform duration-300`}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Conversations</h2>
            <button
              onClick={onToggle}
              className="lg:hidden p-1 text-gray-500 hover:text-gray-700 rounded"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <button
            onClick={onNewConversation}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              <svg className="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Start a new chat to begin</p>
            </div>
          ) : (
            <div className="p-3 space-y-1">
              {groupConversationsByDate().map(([groupName, groupConversations]) => (
                <div key={groupName} className="mb-4">
                  <h3 className="text-xs font-semibold text-gray-500 uppercase px-3 mb-2">
                    {groupName}
                  </h3>
                  {groupConversations.map((conv) => (
                    <div
                      key={conv.id}
                      className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                        conv.id === currentConversationId
                          ? "bg-blue-50 text-blue-900"
                          : "hover:bg-gray-100 text-gray-700"
                      }`}
                      onClick={() => onLoadConversation(conv)}
                    >
                      <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                      </svg>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{conv.title}</p>
                        <p className="text-xs text-gray-500 truncate">{conv.lastMessage}</p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm("Delete this conversation?")) {
                            onDeleteConversation(conv.id);
                          }
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-600 rounded transition-all"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            {conversations.length} conversation{conversations.length !== 1 ? "s" : ""}
          </div>
        </div>
      </div>
    </>
  );
}
